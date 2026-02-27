import time
from typing import Any

from interswitch.auth.async_token_manager import AsyncTokenManager
from interswitch.config import Config
from interswitch.exceptions import APIError, NetworkError, RateLimitError, ValidationError
from interswitch.http_client.base import BaseHttpRequest, Methods, logger
from interswitch.interswitch_types import APIResponse
from interswitch.permissions import check_api_actions

try:
    import httpx
except ImportError as e:
    raise ImportError(
        "The async client requires httpx. Install it using `pip install your-package[async]`"
    ) from e


class AsyncRequest(BaseHttpRequest):
    """Handles all Asynchronous HTTP requests to the Interswitch API using httpx."""

    def __init__(self, config: Config, token_manager: AsyncTokenManager) -> None:
        self.token_manager = token_manager
        self.config = config
        self.base_url = self.config.base_url
        self.timeout = config.request_timeout

        self.session = httpx.AsyncClient(
            timeout=self.timeout, headers={"Content-Type": "application/json"}
        )

    async def request(
        self,
        method: Methods,
        *,
        endpoint: str,
        data: Any = None,
        params: dict[str, Any] | None = None,
        required_actions: str | list[str] | None = None,
    ) -> APIResponse:
        """Make an authenticated asynchronous request to the API."""
        url = f"{self.base_url}{endpoint}"

        logger.debug("%s %s params=%s", method.value, url, params)

        try:
            headers = await self.token_manager.get_auth_header()

            if required_actions:
                available_actions = self.token_manager.get_api_actions()
                check_api_actions(required_actions, available_actions)

            start = time.monotonic()

            response = await self.session.request(
                method=method.value,
                url=url,
                json=data,
                params=params,
                headers=headers,
            )

            elapsed = time.monotonic() - start
            logger.debug("%s %s → %s (%.2fs)", method.value, url, response.status_code, elapsed)

            # Auto-refresh token on 401 Unauthorized
            if response.status_code == 401:
                logger.warning(
                    "Received 401 for %s %s, refreshing token and retrying", method.value, url
                )
                await self.token_manager.refresh_token()
                headers = await self.token_manager.get_auth_header()

                start = time.monotonic()

                response = await self.session.request(
                    method=method.value,
                    url=url,
                    json=data,
                    params=params,
                    headers=headers,
                )
                elapsed = time.monotonic() - start

                logger.debug("%s %s → %s (%.2fs)", method.value, url, response.status_code, elapsed)

            status_code = response.status_code

            # rate limiting error
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

            response_data = response.json() if response.content else {}
            normalized_data = self._normalize_response(response_data, status_code)

            if not normalized_data.get("success", False):
                logger.warning(
                    "API error for %s %s: %s", method.value, url, normalized_data.get("message")
                )
                raise APIError(
                    message=normalized_data.get("message", "API request failed"),
                    status_code=normalized_data.get("code", str(status_code)),
                    reason=normalized_data.get("errors", ["Unknown error"]),
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
        except httpx.TimeoutException as e:
            logger.error("Request timed out for %s %s", method.value, url)
            raise NetworkError(
                message="Request timed out",
                reason=f"Connection timeout after {self.timeout} seconds",
            ) from e
        except httpx.RequestError as e:
            logger.error("Request failed for %s %s: %s", method.value, url, str(e))
            raise NetworkError(
                message="Network request failed",
                reason=str(e),
            ) from e

    async def get(
        self,
        *,
        endpoint: str,
        data: Any = None,
        params: dict[str, Any] | None = None,
        required_actions: str | list[str] | None = None,
    ) -> APIResponse:
        return await self.request(
            Methods.GET,
            endpoint=endpoint,
            data=data,
            params=params,
            required_actions=required_actions,
        )

    async def post(
        self, *, endpoint: str, data: Any = None, required_actions: str | list[str] | None = None
    ) -> APIResponse:
        return await self.request(
            Methods.POST,
            endpoint=endpoint,
            data=data,
            required_actions=required_actions,
        )

    async def aclose(self) -> None:
        """Properly close the underlying httpx session connections."""
        logger.debug("Closing async HTTP session")
        await self.session.aclose()
