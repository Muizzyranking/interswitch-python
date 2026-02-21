"""Pytest configuration and fixtures."""

import os
from unittest.mock import Mock

import pytest

from interswitch import InterswitchClient


@pytest.fixture
def mock_credentials():
    """Mock Interswitch credentials for testing."""
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
    }


@pytest.fixture
def client(mock_credentials, monkeypatch):
    """Create a test client with mocked credentials."""
    monkeypatch.setenv("INTERSWITCH_CLIENT_ID", mock_credentials["client_id"])
    monkeypatch.setenv("INTERSWITCH_CLIENT_SECRET", mock_credentials["client_secret"])

    return InterswitchClient()


@pytest.fixture
def client_with_params(mock_credentials):
    """Create a test client with direct parameters."""
    return InterswitchClient(
        client_id=mock_credentials["client_id"],
        client_secret=mock_credentials["client_secret"],
    )
