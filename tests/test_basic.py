"""Basic smoke tests for the SDK."""

import pytest

from interswitch import InterswitchClient
from interswitch.exceptions import ConfigurationError


def test_imports():
    """Test that imports work correctly."""
    from interswitch import (
        APIError,
        AuthenticationError,
        Config,
        ConfigurationError,
        InterswitchClient,
        InterswitchError,
        NetworkError,
        RateLimitError,
        ValidationError,
    )

    assert InterswitchClient is not None
    assert Config is not None


def test_client_initialization_without_credentials():
    """Test that client raises ConfigurationError without credentials."""
    with pytest.raises(ConfigurationError) as exc_info:
        client = InterswitchClient()

    assert "Client ID not found" in str(exc_info.value)


def test_client_initialization_with_params(mock_credentials):
    """Test client initialization with direct parameters."""
    client = InterswitchClient(
        client_id=mock_credentials["client_id"],
        client_secret=mock_credentials["client_secret"],
    )

    assert client.config.client_id == mock_credentials["client_id"]
    assert client.config.client_secret == mock_credentials["client_secret"]
    assert "InterswitchClient" in repr(client)


def test_client_initialization_with_env(client):
    """Test client initialization from environment variables."""
    assert client is not None
    assert client.config.client_id == "test_client_id"
