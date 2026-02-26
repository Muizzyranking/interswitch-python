import logging
from enum import Enum
from typing import Any

logger = logging.getLogger("interswitch.http_client")

ERROR_RESPONSE_CODE = "ERROR"


class Methods(Enum):
    """HTTP methods supported by the transport layer."""

    POST = "POST"
    GET = "GET"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class BaseHttpRequest:
    """
    Shared logic for API request (sync/async).
    Handles data normalization and standard formatting.
    """

    def _normalize_response(
        self, response_data: dict[str, Any], status_code: int | str
    ) -> dict[str, Any]:
        """Normalize API response to ensure a uniform schema with 'success' field."""
        if response_data.get("responseCode") == ERROR_RESPONSE_CODE:
            return {
                "success": False,
                "code": ERROR_RESPONSE_CODE,
                "status_code": status_code,
                "message": response_data.get("message", ""),
                "logId": response_data.get("logId", None),
                "errors": response_data.get("errors", []),
                "data": response_data.get("data", None),
            }

        if "success" in response_data:
            response_data["status_code"] = status_code
            return response_data

        return {
            "success": int(status_code) < 400,
            "code": response_data.get("responseCode", str(status_code)),
            "status_code": status_code,
            "message": response_data.get("message", "Request processed"),
            "data": response_data.get("data"),
        }
