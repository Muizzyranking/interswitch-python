# Interswitch Python SDK

A robust, fully-typed Python SDK for integrating with the Interswitch API. This library provides both synchronous and asynchronous clients, automatic token management (with auto-refresh), and comprehensive error handling.

---

## ✨ Features

* 🚀 **Dual Clients** — Support for both synchronous (`requests`) and asynchronous (`httpx`) operations
* 🔐 **Auto Token Management** — Automatically fetches, caches, and refreshes OAuth2 tokens
* 🛡️ **Strictly Typed** — Fully type-hinted for excellent IDE support and static analysis
* 📦 **Comprehensive Coverage** — Includes:

  * Identity Verification (NIN, BVN, Passport, Driver's License)
  * CAC Lookups
  * Address Verification
  * AML/PEP checks
  * Value Added Services (VAS)

---

## 🔑 Prerequisites: Getting Your API Keys

Before using this SDK, register on the Interswitch Developer Portal to obtain your credentials:

1. Visit the [Interswitch Developer Console](https://developer.interswitchapp.com/)
2. Create an account or log in
3. Create a new project/application
4. Locate your **Client ID** and **Client Secret** in the project settings

---

# 📦 Installation

## Recommended: Using `uv` (Fast & Modern)

### Standard (Synchronous) Installation

```bash
uv add interswitch-python
```

### Asynchronous Installation (includes `httpx`)

```bash
uv add "interswitch-python[async]"
```

---

## Alternative: Using `pip` (Traditional)

### Standard (Synchronous) Installation

```bash
pip install interswitch-python
```

### Asynchronous Installation

```bash
pip install "interswitch-python[async]"
```

---

# ⚙️ Configuration

Both `InterswitchClient` and `AsyncInterswitchClient` accept the following configuration options during initialization:

| Setting           | Type  | Default                                                                  | Description                                   |
| ----------------- | ----- | ------------------------------------------------------------------------ | --------------------------------------------- |
| `client_id`       | `str` | None                                                                     | Your Interswitch Client ID (**required**)     |
| `client_secret`   | `str` | None                                                                     | Your Interswitch Client Secret (**required**) |
| `base_url`        | `str` | `"https://api-marketplace-routing.k8.isw.la/marketplace-routing/api/v1"` | API base URL                                  |
| `token_url`       | `str` | `"https://passport.interswitchng.com/passport/oauth/token"`              | OAuth token endpoint                          |
| `token_expiry`    | `int` | `3599`                                                                   | Token expiration time (seconds)               |
| `request_timeout` | `int` | `30`                                                                     | HTTP request timeout (seconds)                |

> ⚠️ **Security Note:**
> Always store your `client_id` and `client_secret` in environment variables — never hardcode them.

---

# 🚀 Quick Start

> All SDK method arguments are **keyword-only** to prevent accidental parameter swapping.

---

## 🖥️ Synchronous Usage

```python
import os
from interswitch import InterswitchClient

client = InterswitchClient(
    client_id=os.getenv("INTERSWITCH_CLIENT_ID"),
    client_secret=os.getenv("INTERSWITCH_CLIENT_SECRET"),
    # Optional overrides:
    # request_timeout=60,
    # base_url="https://custom-env.interswitch.com/api/v1"
)

# Verify a National Identity Number (NIN)
response = client.verify_nin(
    nin="12345678901",
    first_name="John",
    last_name="Doe"
)

if response.success:
    print(f"Verification Successful: {response.data}")
else:
    print(f"Verification Failed: {response.message}")
```

---

## ⚡ Asynchronous Usage (Ideal for FastAPI)

> Requires installation with the `[async]` extra.

```python
import os
import asyncio
from interswitch import AsyncInterswitchClient

async def main():
    async with AsyncInterswitchClient(
        client_id=os.getenv("INTERSWITCH_CLIENT_ID"),
        client_secret=os.getenv("INTERSWITCH_CLIENT_SECRET")
    ) as client:

        # Verify a Bank Account
        response = await client.verify_bank_account(
            account_number="0123456789",
            bank_code="058"
        )

        if response.success:
            print("Account Verified!")
            print(response.data)

if __name__ == "__main__":
    asyncio.run(main())
```

---

# 🛑 Error Handling

The SDK provides structured exceptions for clean failure handling:

* `InterswitchError` — Base exception for all SDK errors
* `AuthenticationError` — Token generation or refresh failure
* `ValidationError` — API returned HTTP 400
* `RateLimitError` — API rate limit exceeded (HTTP 429)
* `NetworkError` — Timeout or connection failure

Example:

```python
from interswitch.exceptions import ValidationError, InterswitchError

try:
    client.verify_tin(tin="invalid-tin")
except ValidationError as e:
    print(f"Bad Request: {e.message}")
except InterswitchError as e:
    print(f"API Error: {e.message}")
```

---

# 📚 Documentation

Extensive documentation covering:

* All available endpoints
* Detailed response schemas
* Advanced usage examples

Coming soon.

---

# 📄 License

MIT License

---
