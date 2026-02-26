import logging
import time
from typing import Any

import requests

from interswitch.auth.sync_token_manager import TokenManager
from interswitch.config import Config
from interswitch.exceptions import APIError, NetworkError, RateLimitError, ValidationError
from interswitch.http_client.base import BaseHttpRequest, Methods
from interswitch.interswitch_types import APIResponse

logger = logging.getLogger("interswitch.http_client")


class SyncRequest(BaseHttpRequest):
    """Handles all Synchronous HTTP requests to the Interswitch API using requests."""

    def __init__(self, config: Config, token_manager: TokenManager) -> None:
        self.token_manager = token_manager
        self.config = config
        self.base_url = self.config.base_url
        self.timeout = config.request_timeout

        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def request(
        self,
        method: Methods,
        *,
        endpoint: str,
        data: Any = None,
        params: dict[str, Any] | None = None,
    ) -> APIResponse:
        """Make an authenticated synchronous request to the API."""
        url = f"{self.base_url}{endpoint}"

        logger.debug("%s %s params=%s", method.value, url, params)

        try:
            headers = self.token_manager.get_auth_header()

            start = time.monotonic()

            response = self.session.request(
                method=method.value,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )

            elapsed = time.monotonic() - start

            logger.debug(
                "%s %s → %s (%.2fs)",
                method.value,
                url,
                response.status_code,
                elapsed,
            )

            # Auto-refresh token on 401 Unauthorized
            if response.status_code == 401:
                logger.warning(
                    "Received 401 for %s %s, refreshing token and retrying",
                    method.value,
                    url,
                )
                self.token_manager.invalidate_token()
                headers = self.token_manager.get_auth_header()
                start = time.monotonic()

                response = self.session.request(
                    method=method.value,
                    url=url,
                    json=data,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                )
                elapsed = time.monotonic() - start
                logger.debug(
                    "%s %s → %s (%.2fs) [retry after 401]",
                    method.value,
                    url,
                    response.status_code,
                    elapsed,
                )

            status_code = response.status_code

            if status_code == 429:
                logger.warning("Rate limit exceeded for %s %s", method.value, url)
                raise RateLimitError(
                    message="API rate limit exceeded",
                    status_code="429",
                    reason="Too many requests",
                    response_data=response.json() if response.content else None,
                )

            if status_code == 400:
                error_data = response.json() if response.content else {}
                logger.warning(
                    "Validation error for %s %s: %s", method.value, url, error_data.get("message")
                )
                raise ValidationError(
                    message=error_data.get("message", "Validation failed"),
                    status_code=str(response.status_code),
                    reason=error_data.get("error", "Bad request"),
                    response_data=error_data,
                )

            if response.status_code >= 500:
                logger.error("Server error %s for %s %s", status_code, method.value, url)
                raise NetworkError(
                    message="Server error occurred", reason=f"Server return {response.status_code}"
                )

            # Normalization
            response_data = response.json() if response.content else {}
            normalized_data = self._normalize_response(response_data, status_code)

            if not normalized_data.get("success", False):
                logger.warning(
                    "API error for %s %s: %s", method.value, url, normalized_data.get("message")
                )
                raise APIError(
                    message=normalized_data.get("message", "API request failed"),
                    status_code=normalized_data.get("code", str(response.status_code)),
                    reason=normalized_data.get("error", "Unknown error"),
                    response_data=normalized_data,
                )

            logger.debug("%s %s succeeded: %s", method.value, url, normalized_data.get("message"))

            return APIResponse(
                status_code=str(normalized_data["status_code"]),
                success=normalized_data["success"],
                code=normalized_data["code"],
                message=normalized_data["message"],
                data=normalized_data.get("data"),
            )
        except (RateLimitError, ValidationError, NetworkError, APIError):
            raise

        except requests.exceptions.Timeout as e:
            logger.error("Request timed out for %s %s", method.value, url)
            raise NetworkError(
                message="Request timed out",
                reason=f"Connection timeout after {self.timeout} seconds",
            ) from e
        except requests.exceptions.ConnectionError as e:
            logger.error("Connection failed for %s %s: %s", method.value, url, str(e))
            raise NetworkError(
                message="Connection failed",
                reason=str(e),
            ) from e
        except requests.exceptions.RequestException as e:
            logger.error("Request failed for %s %s: %s", method.value, url, str(e))
            raise NetworkError(message="Network request failed", reason=str(e)) from e

    def get(
        self,
        *,
        endpoint: str,
        data: Any = None,
        params: dict[str, Any] | None = None,
    ) -> APIResponse:
        return self.request(Methods.GET, endpoint=endpoint, data=data, params=params)

    def post(self, *, endpoint: str, data: Any = None) -> APIResponse:
        return self.request(Methods.POST, endpoint=endpoint, data=data)

    def close(self) -> None:
        """Close the session to free up resources."""
        self.session.close()
