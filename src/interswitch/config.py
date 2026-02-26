"""
Configuration management for Interswitch SDK.
Supports environment variables, direct parameters, and Django settings.
"""

import os
from typing import Any


class Config:
    """
    Configuration handler with support for multiple sources.

    Priority order (highest to lowest):
    1. Direct parameters passed to client
    2. Django settings (if available)
    3. Environment variables
    """

    # Environment variable names
    ENV_CLIENT_ID = "INTERSWITCH_CLIENT_ID"
    ENV_CLIENT_SECRET = "INTERSWITCH_CLIENT_SECRET"
    ENV_BASE_URL = "INTERSWITCH_BASE_URL"
    ENV_TOKEN_URL = "INTERSWITCH_TOKEN_URL"
    ENV_TOKEN_EXP = "INTERSWITCH_TOKEN_EXPIRY"
    ENV_REQUEST_TIMEOUT = "INTERSWITCH_REQUEST_TIMEOUT"

    DJANGO_CLIENT_ID = "INTERSWITCH_CLIENT_ID"
    DJANGO_CLIENT_SECRET = "INTERSWITCH_CLIENT_SECRET"
    DJANGO_BASE_URL = "INTERSWITCH_BASE_URL"
    DJANGO_TOKEN_URL = "INTERSWITCH_TOKEN_URL"
    DJANGO_TOKEN_EXP = "INTERSWITCH_TOKEN_EXPIRY"
    DJANGO_REQUEST_TIMEOUT = "INTERSWITCH_REQUEST_TIMEOUT"

    # DEFAULT_BASE_URL = "https://api-marketplace-routing.k8.isw.la"
    DEFAULT_BASE_URL = "https://api-marketplace-routing.k8.isw.la/marketplace-routing/api/v1"
    DEFAULT_TOKEN_URL = "https://qa.interswitchng.com/passport/oauth/token"
    DEFAULT_TOKEN_EXPIRY = 1799
    DEFFAULT_REQUEST_TIMEOUT = 30

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        base_url: str | None = None,
        token_url: str | None = None,
        token_expiry: int | None = None,
        request_timeout: int | None = None,
    ) -> None:
        """
        Initialize configuration.
        """
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = base_url
        self._token_url = token_url
        self._token_expiry = token_expiry
        self._request_timeout = request_timeout

        self._django_settings: Any = None
        self._django_available = self._check_django()

    def _check_django(self) -> bool:
        """Check if Django is available and configured."""
        try:
            from django.conf import settings  # type: ignore

            if settings.configured:
                self._django_settings = settings
                return True
        except ImportError:
            pass
        return False

    def _get_from_django(self, key: str) -> str | None:
        """Get value from Django settings if available."""
        if self._django_available and self._django_settings:
            return getattr(self._django_settings, key, None)
        return None

    def _get_from_env(self, key: str) -> str | None:
        """Get value from environment variables."""
        return os.environ.get(key)

    @property
    def client_id(self) -> str:
        """
        Get client ID from configuration sources.
        """
        from interswitch.exceptions import ConfigurationError

        # Priority: direct param > Django > env
        value = (
            self._client_id
            or self._get_from_django(self.DJANGO_CLIENT_ID)
            or self._get_from_env(self.ENV_CLIENT_ID)
        )

        if not value:
            raise ConfigurationError(
                "Client ID not found. Please provide it via parameter, "
                f"Django settings ({self.DJANGO_CLIENT_ID}), "
                f"or environment variable ({self.ENV_CLIENT_ID})."
            )

        return value

    @property
    def client_secret(self) -> str:
        """
        Get client secret from configuration sources.
        """
        from interswitch.exceptions import ConfigurationError

        # Priority: direct param > Django > env
        value = (
            self._client_secret
            or self._get_from_django(self.DJANGO_CLIENT_SECRET)
            or self._get_from_env(self.ENV_CLIENT_SECRET)
        )

        if not value:
            raise ConfigurationError(
                "Client secret not found. Please provide it via parameter, "
                f"Django settings ({self.DJANGO_CLIENT_SECRET}), "
                f"or environment variable ({self.ENV_CLIENT_SECRET})."
            )

        return value

    @property
    def base_url(self) -> str:
        """
        Get base URL from configuration sources.
        """
        # Priority: direct param > Django > env > default
        return (
            self._base_url
            or self._get_from_django(self.DJANGO_BASE_URL)
            or self._get_from_env(self.ENV_BASE_URL)
            or self.DEFAULT_BASE_URL
        )

    @property
    def token_url(self) -> str:
        """Get OAuth token URL (currently fixed)."""
        return (
            self._token_url
            or self._get_from_django(self.DJANGO_TOKEN_URL)
            or self._get_from_env(self.ENV_TOKEN_URL)
            or self.DEFAULT_TOKEN_URL
        )

    @property
    def token_expiry(self) -> int:
        if self._token_expiry is not None:
            return int(self._token_expiry)
        from_django = self._get_from_django(self.DJANGO_TOKEN_EXP)
        if from_django is not None:
            return int(from_django)
        from_env = self._get_from_env(self.ENV_TOKEN_EXP)
        if from_env is not None:
            return int(from_env)
        return self.DEFAULT_TOKEN_EXPIRY

    @property
    def request_timeout(self) -> int:
        if self._request_timeout is not None:
            return int(self._request_timeout)
        from_django = self._get_from_django(self.DJANGO_REQUEST_TIMEOUT)
        if from_django is not None:
            return int(from_django)
        from_env = self._get_from_env(self.ENV_REQUEST_TIMEOUT)
        if from_env is not None:
            return int(from_env)
        return self.DEFFAULT_REQUEST_TIMEOUT

    def is_configured(self) -> bool:
        """
        Check if minimum configuration is available.
        """
        try:
            _ = self.client_id
            _ = self.client_secret
            return True
        except Exception:
            return False

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"Config("
            f"client_id={'***' if self._client_id else 'from_source'}, "
            f"base_url={self.base_url!r})"
        )
