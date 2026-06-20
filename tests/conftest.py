"""
Pytest configuration and shared fixtures.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from interswitch import AsyncInterswitchClient, InterswitchClient
from interswitch.auth.async_token_manager import AsyncTokenManager
from interswitch.auth.sync_token_manager import TokenManager
from interswitch.config import Config
from interswitch.http_client.async_request import AsyncRequest
from interswitch.http_client.sync_request import SyncRequest
from interswitch.interswitch_types import APIResponse


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


@pytest.fixture
def config(mock_credentials):
    return Config(
        client_id=mock_credentials["client_id"],
        client_secret=mock_credentials["client_secret"],
    )


@pytest.fixture
def token_manager(config):
    """Sync token manager with a pre-populated valid token."""
    manager = TokenManager(config)
    manager.access_token = "test_access_token"
    manager.token_expiry = datetime.now() + timedelta(hours=1)
    manager.token_data = {
        "access_token": "test_access_token",
        "expires_in": 3600,
        "scope": "profile",
        "client_name": "test-client|TEST",
        "marketplace_user": "test@example.com",
        "api-routing-actions": ["NINService", "BVNService"],
    }
    return manager


@pytest.fixture
def expired_token_manager(config):
    """Sync token manager with a token that is already expired."""
    manager = TokenManager(config)
    manager.access_token = "expired_token"
    manager.token_expiry = datetime.now() - timedelta(seconds=1)
    return manager


@pytest.fixture
def empty_token_manager(config):
    """Sync token manager with no token at all."""
    return TokenManager(config)


@pytest.fixture
def async_token_manager(config):
    """Async token manager with a pre-populated valid token."""
    manager = AsyncTokenManager(config)
    manager.access_token = "test_access_token"
    manager.token_expiry = datetime.now() + timedelta(hours=1)
    manager.token_data = {
        "access_token": "test_access_token",
        "expires_in": 3600,
        "scope": "profile",
        "client_name": "test-client|TEST",
        "marketplace_user": "test@example.com",
        "api-routing-actions": ["NINService"],
    }
    return manager


@pytest.fixture
def sync_http_client(config, token_manager):
    return SyncRequest(config, token_manager)


@pytest.fixture
def async_http_client(config, async_token_manager):
    return AsyncRequest(config, async_token_manager)


@pytest.fixture
def sync_client(config, token_manager):
    """
    InterswitchClient with a pre-seeded token manager.
    Individual tests mock http_client.post / http_client.get as needed.
    """
    c = InterswitchClient(
        client_id=config.client_id,
        client_secret=config.client_secret,
    )
    c.token_manager = token_manager
    c.http_client = SyncRequest(config, token_manager)
    return c


@pytest.fixture
def async_client(config, async_token_manager):
    """
    AsyncInterswitchClient with a pre-seeded token manager.
    Individual tests mock http_client.post / http_client.get as needed.
    """
    c = AsyncInterswitchClient(
        client_id=config.client_id,
        client_secret=config.client_secret,
    )
    c.token_manager = async_token_manager
    c.http_client = AsyncRequest(config, async_token_manager)
    return c


def make_requests_response(status_code=200, json_data=None, has_content=True):
    """Build a mock requests.Response."""
    r = MagicMock()
    r.status_code = status_code
    r.content = b"content" if has_content else b""
    r.json.return_value = json_data or {}
    return r


def make_httpx_response(status_code=200, json_data=None, has_content=True):
    """Build a mock httpx.Response."""
    r = MagicMock()
    r.status_code = status_code
    r.content = b"content" if has_content else b""
    r.json.return_value = json_data or {}
    return r


def make_api_response(data=None, message="request processed successfully"):
    """Return an APIResponse as the SDK would return on success."""
    return APIResponse(
        success=True,
        code="200",
        status_code="200",
        message=message,
        data=data,
    )


def make_success_payload(data=None, message="request processed successfully"):
    """Raw API success payload (as the server sends it)."""
    return {
        "success": True,
        "code": "200",
        "message": message,
        "data": data if data is not None else {},
    }


def make_error_payload(message="Something went wrong", log_id="abc-123"):
    """Raw API error payload (as the server sends it)."""
    return {
        "responseCode": "ERROR",
        "message": message,
        "errors": [],
        "logId": log_id,
    }
