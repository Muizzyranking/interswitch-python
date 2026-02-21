"""
Exception classes for Interswitch SDK.
"""


class InterswitchError(Exception):
    """Base exception for all Interswitch SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: str | None = None,
        response_data: dict | None = None,
        reason: str | None = None,
    ) -> None:
        """
        Initialize Interswitch error.
        """
        self.message = message
        self.reason = reason
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message)

    def __str__(self) -> str:
        """String representation of the error."""
        parts = [self.message]
        if self.status_code:
            parts.append(f"[Code: {self.status_code}]")
        if self.reason:
            parts.append(f"[Reason: {self.reason}]")
        return " ".join(parts)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"code={self.status_code!r}, "
            f"reason={self.reason!r})"
        )


class AuthenticationError(InterswitchError):
    """Raised when authentication fails (token generation, invalid credentials)."""

    pass


class APIError(InterswitchError):
    """Raised when API request fails."""

    pass


class ValidationError(InterswitchError):
    """Raised when request validation fails (missing/invalid parameters)."""

    pass


class RateLimitError(InterswitchError):
    """Raised when API rate limit is exceeded."""

    pass


class NetworkError(InterswitchError):
    """Raised when network/connection issues occur."""

    pass


class ConfigurationError(InterswitchError):
    """Raised when SDK configuration is invalid or missing."""

    pass
