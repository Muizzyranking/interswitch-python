"""
Interswitch Python SDK.

Python SDK for Interswitch APIs to make requests easier.
"""

from interswitch.client import InterswitchClient
from interswitch.config import Config
from interswitch.exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    InterswitchError,
    NetworkError,
    RateLimitError,
    ValidationError,
)

__version__ = "0.1.0"
__all__ = [
    "InterswitchClient",
    "Config",
    # Exceptions
    "InterswitchError",
    "AuthenticationError",
    "APIError",
    "ValidationError",
    "RateLimitError",
    "NetworkError",
    "ConfigurationError",
]
