from enum import Enum
from typing import TypeVar

import requests
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from interswitch.config import Config
from interswitch.exceptions import APIError, NetworkError, RateLimitError, ValidationError
from interswitch.token_manager import TokenManager

T = TypeVar("T", bound=BaseModel)


class Methods(Enum):
    POST = "POST"
    GET = "GET"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class HttpClient:
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
        response_model: type[T],
        data: dict | None = None,
        params: dict | None = None,
    ):
        """
        Make an authenticated request to the API.
        """
        method_value = method.value
        url = f"{self.base_url}{endpoint}"
        try:
            headers = self.token_manager.get_auth_header()

            response = self.session.request(
                method=method_value,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )

            if response.status_code == 401:
                self.token_manager.invalidate_token()
                headers = self.token_manager.get_auth_header()

                response = self.session.request(
                    method=method_value,
                    url=url,
                    json=data,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                )

            if response.status_code == 429:
                raise RateLimitError(
                    message="API rate limit exceeded",
                    status_code="429",
                    reason="Too many requests",
                    response_data=response.json() if response.content else None,
                )

            if response.status_code == 400:
                error_data = response.json() if response.content else {}
                raise ValidationError(
                    message=error_data.get("message", "Validation failed"),
                    status_code=str(response.status_code),
                    reason=error_data.get("error", "Bad request"),
                    response_data=error_data,
                )

            response_data = response.json() if response.content else {}

            if not response_data.get("success", False):
                raise APIError(
                    message=response_data.get("message", "API request failed"),
                    status_code=response_data.get("code", str(response.status_code)),
                    reason=response_data.get("error", "Unknown error"),
                    response_data=response_data,
                )

            try:
                return response_model(**response_data)
            except PydanticValidationError as e:
                raise ValidationError(
                    message="Response validation failed",
                    reason=str(e),
                    response_data=response_data,
                ) from e

        except requests.exceptions.Timeout as e:
            raise NetworkError(
                message="Request timed out",
                reason=f"Connection timeout after {self.timeout} seconds",
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(
                message="Connection failed",
                reason=str(e),
            ) from e
        except requests.exceptions.RequestException as e:
            if not isinstance(e, (ValidationError, RateLimitError, APIError)):
                raise NetworkError(
                    message="Network request failed",
                    reason=str(e),
                ) from e
            raise

    def get(
        self,
        *,
        endpoint: str,
        response_model: type[T],
        data: dict | None = None,
        params: dict | None = None,
    ) -> T:
        return self.request(
            Methods.GET,
            endpoint=endpoint,
            response_model=response_model,
            data=data,
            params=params,
        )

    def post(
        self,
        *,
        endpoint: str,
        response_model: type[T],
        data: dict | None = None,
    ) -> T:
        return self.request(
            Methods.POST,
            endpoint=endpoint,
            response_model=response_model,
            data=data,
        )
