"""Response types."""

from dataclasses import dataclass
from typing import Any


@dataclass
class TokenResponse:
    access_token: str
    token_type: str
    expires_in: int
    scope: str
    marketplace_user: str
    client_name: str
    client_description: str
    jti: str
    client_logo: str | None = None


@dataclass
class TokenInfo:
    is_valid: bool
    expires_at: str | None
    client_name: str | None
    marketplace_user: str | None
    scope: list[str] | None
    api_actions: list[str]


@dataclass
class APIResponse:
    success: bool
    code: str
    status_code: str | int
    message: str
    data: Any = None


@dataclass
class ErrorResponse:
    success: bool = False
    code: str = "Error"
    message: str = ""
    logId: str | None = None
    errors: list[Any] | None = None
    data: Any = None
