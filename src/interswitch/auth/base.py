import base64
import logging
from datetime import datetime, timedelta
from typing import Any

from interswitch.config import Config

logger = logging.getLogger("interswitch.auth")


class BaseTokenManager:
    """
    Core token logic shared between Sync and Async implementations.
    Handles state, expiration, and invalidation without doing I/O.
    """

    def __init__(self, config: Config) -> None:
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.token_url = config.token_url
        self.default_token_expiry = config.token_expiry
        self.request_timeout = config.request_timeout

        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.authorization_header = f"Basic {encoded_credentials}"

        self.access_token: str | None = None
        self.token_expiry: datetime | None = None
        self.token_data: dict[str, Any] | None = None
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": self.authorization_header,
        }

        self.data = {"scope": "profile", "grant_type": "client_credentials"}
        logger.debug("Token manager initialized for client_id=%s", self.client_id)

    def is_token_valid(self) -> bool:
        """Check if the current token is still valid."""
        if not self.access_token or not self.token_expiry:
            return False
        return datetime.now() < self.token_expiry

    def _process_new_token_data(self, token_data: dict[str, Any]) -> None:
        """Shared logic to update state when a new token is fetched."""
        self.access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in", self.default_token_expiry)

        # Buffer of 60 seconds before actual expiry
        self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)
        self.token_data = token_data

        logger.info(
            "Token refreshed successfully, expires_at=%s",
            self.token_expiry.isoformat(),
        )

    def invalidate_token(self) -> None:
        """Force token invalidation."""
        logger.debug("Token invalidated manually")
        self.access_token = None
        self.token_expiry = None
        self.token_data = None

    def get_token_info(self) -> dict[str, Any]:
        """Get information about the current token."""
        if not self.token_data:
            return {"status": "no_token", "is_valid": False}

        return {
            "is_valid": self.is_token_valid(),
            "expires_at": self.token_expiry.isoformat() if self.token_expiry else None,
            "client_name": self.token_data.get("client_name"),
            "marketplace_user": self.token_data.get("marketplace_user"),
            "scope": self.token_data.get("scope"),
            "api_actions": self.token_data.get("api-routing-actions", []),
        }

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"<{self.__class__.__name__} "
            f"valid={self.is_token_valid()} "
            f"expires_at={self.token_expiry.isoformat() if self.token_expiry else None}>"
        )
