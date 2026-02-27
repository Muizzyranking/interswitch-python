# interswitch-python

A Python SDK for the [Interswitch API Marketplace](https://developer.interswitchgroup.com/). Supports identity verification, AML/PEP checks, address verification, SafeToken OTP, CAC lookups, BVN services, and bills payment — with both synchronous and asynchronous clients.

---

## Features

- **Sync & Async** — use `InterswitchClient` for standard Python apps, `AsyncInterswitchClient` for FastAPI, asyncio, and other async frameworks
- **Auto token management** — OAuth2 tokens are fetched, cached, and refreshed automatically
- **Django integration** — configure via Django settings instead of environment variables
- **Typed responses** — all methods return a consistent `APIResponse` dataclass
- **Structured exceptions** — specific exception types for auth errors, validation errors, rate limits, and network failures

---

## Requirements

- Python 3.10+
- An Interswitch Marketplace account with an active project ([sign up here](https://developer.interswitchgroup.com/))

---

## Installation

```bash
# using uv (recommended)
# Sync only
uv add interswitch-python

# or using pip

pip install interswitch-python

# With async support (includes httpx)
uv add "interswitch-python[async]"

# or using pip

pip install interswitch-python[async]
```

---

## Quick Start

### Get your credentials

1. Go to [Interswitch API Marketplace](https://developer.interswitchgroup.com/)
2. Create an account and log in
3. Create a new project
4. Select the APIs of interest in the project
5. Copy your **Client ID** and **Client Secret**

### Synchronous usage

```python
from interswitch import InterswitchClient

client = InterswitchClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
)

response = client.verify_bvn_boolean(
    bvn="12345678901",
    first_name="John",
    last_name="Doe",
)

if response.success:
    print(response.data)
```

### Async usage

```python
import asyncio
from interswitch import AsyncInterswitchClient

async def main():
    async with AsyncInterswitchClient(
        client_id="your-client-id",
        client_secret="your-client-secret",
    ) as client:
        response = await client.verify_nin(
            nin="12345678901",
            first_name="John",
            last_name="Doe",
        )
        print(response.data)

asyncio.run(main())
```

---

## Configuration

Credentials can be provided in three ways (highest priority first):

### 1. Direct parameters

```python
client = InterswitchClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
)
```

### 2. Environment variables

```bash
export INTERSWITCH_CLIENT_ID="your-client-id"
export INTERSWITCH_CLIENT_SECRET="your-client-secret"
```

```python
client = InterswitchClient()  # picks up from environment
```

### 3. Django settings

```python
# settings.py
INTERSWITCH_CLIENT_ID = "your-client-id"
INTERSWITCH_CLIENT_SECRET = "your-client-secret"
```

```python
client = InterswitchClient()  # picks up from Django settings
```

### Optional configuration

```python
client = InterswitchClient(
    client_id="...",
    client_secret="...",
    base_url="https://your-production-url",   # override base URL
    token_url="https://your-token-url",       # override token URL
    token_expiry=1799,                        # token cache duration in seconds
    request_timeout=30,                       # HTTP timeout in seconds
)
```

---

## Response format

All methods return an `APIResponse` dataclass:

```python
@dataclass
class APIResponse:
    success: bool       # True if request succeeded
    code: str           # Response code (e.g. "200")
    status_code: str    # HTTP status code
    message: str        # Human-readable message
    data: Any           # Response payload (varies by endpoint)
```

---

## Error handling

```python
from interswitch import InterswitchClient
from interswitch.exceptions import (
    AuthenticationError,   # Invalid credentials or token failure
    ValidationError,       # Invalid request parameters (HTTP 400)
    RateLimitError,        # Too many requests (HTTP 429)
    NetworkError,          # Connection or timeout failure
    APIError,              # API-level error in response body
    ConfigurationError,    # Missing client_id or client_secret
)

client = InterswitchClient(client_id="...", client_secret="...")

try:
    response = client.verify_nin(
        nin="00000000000",
        first_name="John",
        last_name="Doe",
    )
except ValidationError as e:
    print(f"Bad request: {e.message}")
except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
except RateLimitError:
    print("Rate limit hit, retry later")
except NetworkError as e:
    print(f"Network issue: {e.reason}")
except APIError as e:
    print(f"API error: {e.message} (code: {e.status_code})")
```

---

## Available APIs

| Category | Methods |
|---|---|
| Identity Verification | `verify_nin`, `verify_nin_full`, `verify_bvn_boolean`, `verify_bvn_full`, `verify_bank_account`, `verify_tin`, `verify_drivers_license`, `verify_intl_passport`, `get_bank_list` |
| AML / PEP / Biometrics | `verify_domestic_pep`, `verify_global_aml`, `compare_faces` |
| Address Verification | `submit_physical_address`, `get_physical_address` |
| SafeToken OTP | `generate_safetoken`, `send_safetoken`, `verify_safetoken` |
| CAC Lookup | `lookup_cac`, `lookup_cac_directors`, `lookup_cac_secretary`, `lookup_cac_shareholders` |
| BVN Accounts Lookup | `initiate_bvn_accounts_lookup`, `request_bvn_accounts_otp`, `fetch_bvn_accounts_details` |
| BVN iGree | `initiate_bvn_igree`, `request_bvn_igree_otp`, `fetch_bvn_igree_details` |
| Credit History | `lookup_credit_history` |
| Bills Payment (VAS) | `get_vas_billers`, `get_vas_payment_item`, `validate_vas_customer`, `pay_vas`, `get_vas_transactions` |

---

## Documentation

Full documentation is available in the [`docs/`](./docs) directory:

- [Getting Started](./docs/getting-started.md)
- [Configuration](./docs/configuration.md)
- [Error Handling](./docs/error-handling.md)
- [API Reference](./docs/api-reference.md)
- [Async Usage](./docs/async.md)
- [Django Integration](./docs/django.md)

---

## License

MIT
