import threading
from typing import Any

import requests

from interswitch.auth.base import BaseTokenManager, logger
from interswitch.config import Config
from interswitch.exceptions import AuthenticationError


class TokenManager(BaseTokenManager):
    """
    Synchronous Token Manager using requests.
    """

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self._lock: threading.Lock | None = None

    def _get_lock(self) -> threading.Lock:
        if self._lock is None:
            self._lock = threading.Lock()
        return self._lock

    def _fetch_new_token(self) -> dict[str, Any]:
        """Request a new access token from the authentication server."""
        logger.debug("Requesting new token from %s", self.token_url)
        try:
            response = requests.post(
                self.token_url, headers=self.headers, data=self.data, timeout=self.request_timeout
            )
            response.raise_for_status()

            token_data = response.json()
            self._process_new_token_data(token_data)

            return token_data

        except requests.exceptions.RequestException as e:
            logger.error("Token request failed: %s", str(e))
            error_msg = f"Token request failed: {str(e)}"
            raise AuthenticationError(
                message=error_msg,
                reason=str(e),
                response_data=getattr(e.response, "json", lambda: None)()
                if hasattr(e, "response")
                else None,
            ) from e

    def get_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        if self.is_token_valid() and self.access_token:
            logger.debug("Using cached token, expires_at=%s", self.token_expiry)
            return self.access_token

        lock = self._get_lock()

        with lock:
            if self.is_token_valid() and self.access_token:
                logger.debug("Token was refreshed by another thread, reusing")
                return self.access_token

            logger.debug("Token expired or missing, fetching new token")
            self._fetch_new_token()

        if not self.access_token:
            raise AuthenticationError(
                message="Failed to obtain access token",
                reason="Token is None after refresh attempt",
            )

        return self.access_token

    def get_auth_header(self) -> dict[str, str]:
        """Get authorization header with a valid bearer token."""
        token = self.get_token()
        return {"Authorization": f"Bearer {token}"}
