# Configuration

## Priority order

Configuration is resolved in this order — earlier sources win:

1. Direct parameters passed to `InterswitchClient(...)`
2. Django settings (if Django is installed and configured)
3. Environment variables
4. Defaults

---

## Environment variables

| Variable | Description | Default |
|---|---|---|
| `INTERSWITCH_CLIENT_ID` | Your Client ID | — |
| `INTERSWITCH_CLIENT_SECRET` | Your Client Secret | — |
| `INTERSWITCH_BASE_URL` | API base URL | QA URL |
| `INTERSWITCH_TOKEN_URL` | OAuth token URL | QA passport URL |
| `INTERSWITCH_TOKEN_EXPIRY` | Token lifetime in seconds | 1799 |
| `INTERSWITCH_REQUEST_TIMEOUT` | HTTP timeout in seconds | 30 |

---

## Direct parameters

```python
from interswitch import InterswitchClient

client = InterswitchClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
    base_url="https://qa.interswitchng.com",      # optional
    token_url="https://passport.interswitchng.com/passport/oauth/token",  # optional
    token_expiry=1799,                             # optional
    request_timeout=30,                            # optional
)
```

---

## Django settings

Add to your `settings.py`:

```python
INTERSWITCH = {
    "CLIENT_ID": "your-client-id",
    "CLIENT_SECRET": "your-client-secret",
    "BASE_URL": "https://qa.interswitchng.com",       # optional
    "TOKEN_URL": "https://passport.interswitchng.com/passport/oauth/token",  # optional
    "TOKEN_EXPIRY": 1799,                              # optional
    "REQUEST_TIMEOUT": 30,                             # optional
}
```

The client picks these up automatically with no extra configuration.

---
## Using .env files

```python
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env file into environment variables

client = InterswitchClient() # auto-picks up environment variables

# or pass in directly

client = InterswitchClient(
    client_id=os.getenv("INTERSWITCH_CLIENT_ID"),
    client_secret=os.getenv("INTERSWITCH_CLIENT_SECRET"),
)
```

---

## Custom Config object

For advanced use — injecting configuration from secrets managers, environment-specific config files, or tests:

```python
from interswitch import InterswitchClient
from interswitch.config import Config

config = Config(
    client_id="your-client-id",
    client_secret="your-client-secret",
)

client = InterswitchClient(config=config)
```

When you pass a `Config` object, all other kwargs are ignored.

---

## Production vs QA

The SDK defaults to QA. When you are ready for production, set both URLs:

```bash
INTERSWITCH_BASE_URL=https://api.interswitchng.com
INTERSWITCH_TOKEN_URL=https://passport.interswitchng.com/passport/oauth/token
```

Or in Django settings:

```python
INTERSWITCH = {
    "CLIENT_ID": env("INTERSWITCH_CLIENT_ID"),
    "CLIENT_SECRET": env("INTERSWITCH_CLIENT_SECRET"),
    "BASE_URL": "https://api.interswitchng.com",
    "TOKEN_URL": "https://passport.interswitchng.com/passport/oauth/token",
}
```

---

## Inspecting the current token

```python
info = client.get_token_info()

print(info["is_valid"])        # True / False
print(info["expires_at"])      # ISO datetime string
print(info["client_name"])     # your project identifier
print(info["marketplace_user"]) # your Marketplace email
print(info["api_actions"])     # list of APIs your token can access
```

`api_actions` is what the SDK checks for scope before every call. If a method fails with `InsufficientScopeError`, compare the required scope in the error against this list to see what is missing.
