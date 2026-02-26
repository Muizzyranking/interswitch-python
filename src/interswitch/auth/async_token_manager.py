import asyncio
from typing import Any

from interswitch.auth.base import BaseTokenManager, logger
from interswitch.config import Config
from interswitch.exceptions import AuthenticationError

try:
    import httpx
except ImportError:
    httpx = None


class AsyncTokenManager(BaseTokenManager):
    """
    Asynchronous Token Manager using httpx.
    Handles token generation and automatic renewal without blocking the event loop.
    """

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self._lock: asyncio.Lock | None = None

    def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def _fetch_new_token(self) -> dict[str, Any]:
        """Request a new access token asynchronously."""
        if httpx is None:
            raise ImportError(
                "The async client requires httpx. Install it using `pip install your-package[async]`"
            )
        logger.debug("Requesting new token from %s", self.token_url)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_url,
                    headers=self.headers,
                    data=self.data,
                    timeout=self.request_timeout,
                )
                response.raise_for_status()

                token_data = response.json()
                self._process_new_token_data(token_data)

                return token_data

            except httpx.RequestError as e:
                logger.error("Token request failed (network): %s", str(e))
                raise AuthenticationError(
                    message=f"Token request failed: {str(e)}",
                    reason=str(e),
                ) from e
            except httpx.HTTPStatusError as e:
                error_data = None
                try:
                    error_data = e.response.json()
                except ValueError:
                    pass
                logger.error(
                    "Token request failed with status %s: %s",
                    e.response.status_code,
                    error_data,
                )

                raise AuthenticationError(
                    message=f"Token request failed with status {e.response.status_code}",
                    reason=str(e),
                    response_data=error_data,
                ) from e

    async def get_token(self) -> str:
        """Get a valid access token asynchronously, refreshing if necessary."""
        if self.is_token_valid() and self.access_token:
            logger.debug("Using cached token, expires_at=%s", self.token_expiry)
            return self.access_token

        lock = self._get_lock()

        async with lock:  # Prevent multiple simultaneous refreshes
            # Double-check after acquiring lock — another coroutine may have
            # already refreshed the token while we were waiting
            if self.is_token_valid() and self.access_token:
                logger.debug("Token was refreshed by another coroutine, reusing")
                return self.access_token

            logger.debug("Token expired or missing, fetching new token")
            await self._fetch_new_token()

        if not self.access_token:
            raise AuthenticationError(
                message="Failed to obtain access token",
                reason="Token is None after refresh attempt",
            )

        return self.access_token

    async def refresh_token(self) -> None:
        lock = self._get_lock()
        async with lock:
            logger.debug("Forcing token refresh due to 401 response")
            self.invalidate_token()
            await self._fetch_new_token()
        if not self.access_token:
            raise AuthenticationError(
                message="Failed to refresh access token",
                reason="Token is None after refresh attempt",
            )

    async def get_auth_header(self) -> dict[str, str]:
        """Get authorization header with a valid bearer token asynchronously."""
        token = await self.get_token()
        return {"Authorization": f"Bearer {token}"}
