"""
OAuth token management with automatic refresh capability.
"""

import base64
from datetime import datetime, timedelta
from typing import Any

import requests

from interswitch.config import Config
from interswitch.exceptions import AuthenticationError


class TokenManager:
    """
    Manages OAuth token authentication with automatic refresh.

    Handles token generation, expiry tracking, and automatic renewal.
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize token manager.

        Args:
            client_id: Interswitch client ID
            client_secret: Interswitch client secret
            token_url: OAuth token endpoint URL
        """
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.token_url = config.token_url
        self.default_token_expiry = config.token_expiry

        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.authorization_header = f"Basic {encoded_credentials}"

        self.access_token: str | None = None
        self.token_expiry: datetime | None = None
        self.token_data: dict[str, Any] | None = None

    def get_new_token(self) -> dict[str, Any]:
        """
        Request a new access token from the authentication server.
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": self.authorization_header,
        }

        data = {"scope": "profile", "grant_type": "client_credentials"}

        try:
            response = requests.post(self.token_url, headers=headers, data=data, timeout=30)
            response.raise_for_status()

            token_data = response.json()

            self.access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", self.default_token_expiry)

            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)
            self.token_data = token_data

            return token_data

        except requests.exceptions.RequestException as e:
            error_msg = f"Token request failed: {str(e)}"
            raise AuthenticationError(
                message=error_msg,
                reason=str(e),
                response_data=getattr(e.response, "json", lambda: None)()
                if hasattr(e, "response")
                else None,
            ) from e

    def is_token_valid(self) -> bool:
        """
        Check if the current token is still valid.
        """
        if not self.access_token or not self.token_expiry:
            return False

        return datetime.now() < self.token_expiry

    def get_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.
        """
        if not self.is_token_valid():
            self.get_new_token()

        if not self.access_token:
            raise AuthenticationError(
                message="Failed to obtain access token",
                reason="Token is None after refresh attempt",
            )

        return self.access_token

    def get_auth_header(self) -> dict[str, str]:
        """
        Get authorization header with a valid bearer token.
        """
        token = self.get_token()
        return {"Authorization": f"Bearer {token}"}

    def invalidate_token(self) -> None:
        """Force token invalidation (useful for testing or manual refresh)."""
        self.access_token = None
        self.token_expiry = None
        self.token_data = None

    def get_token_info(self) -> dict[str, Any]:
        """
        Get information about the current token.
        """
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
            f"TokenManager("
            f"client_id={'***'}, "
            f"token_valid={self.is_token_valid()}, "
            f"expires_at={self.token_expiry.isoformat() if self.token_expiry else None})"
        )
