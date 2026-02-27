# Getting Started

## 1. Create a project on the Interswitch Marketplace

Before anything else, go to [developer.interswitchgroup.com](https://developer.interswitchgroup.com/) and create a project. When creating the project, select the specific APIs you need — NIN, BVN, CAC, VAS, etc.

Your Client ID and Client Secret are scoped to the APIs you selected. If you try to call an API your project does not include, the SDK raises `InsufficientActionsError` before making any network request (more on this in [Error Handling](02-error-handling.md)).

Once you have your credentials, start in the QA environment. All default URLs point to QA. Move to production by setting `base_url` and `token_url` when you are ready.

---

## 2. Install

```bash
# with uv
uv add interswitch-python

# with pip
pip install interswitch-python
```

If you need async support:

```bash
# with uv
uv add interswitch-python[async]

# with pip
pip install interswitch-python[async]
```

---

## 3. Set your credentials

The simplest approach is environment variables:

```bash
export INTERSWITCH_CLIENT_ID=your-client-id
export INTERSWITCH_CLIENT_SECRET=your-client-secret
```

Then initialize the client with no arguments:

```python
from interswitch import InterswitchClient

client = InterswitchClient()
```

Or pass credentials directly:

```python
client = InterswitchClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
)
```

See [Configuration](configuration.md) for all options including Django settings.

---

## 4. Make your first call

```python
from interswitch import InterswitchClient
from interswitch.exceptions import InterswitchError

client = InterswitchClient()

response = client.verify_nin(
    nin="12345678901",
    first_name="Muiz",
    last_name="Yusuf",
)

print(response.success)   # True
print(response.data)      # dict with verification result
```

The client handles authentication automatically. On the first call it fetches a token using your credentials. It caches the token and refreshes it before it expires. You never manage tokens yourself.

---

## 5. Understand the response

Every successful method returns an `APIResponse`:

```python
response.success     # True
response.code        # "200"
response.status_code # "200"
response.message     # "request processed successfully"
response.data        # dict or list — the actual result
```

If the call fails for any reason, an exception is raised — the response is never returned with `success=False`. See [Error Handling](02-error-handling.md).

---

## 6. Handle errors

```python
from interswitch import InterswitchClient
from interswitch.permissions import InsufficientActionsError
from interswitch.exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ValidationError,
)

client = InterswitchClient()

try:
    response = client.verify_nin(
        nin="12345678901",
        first_name="Muiz",
        last_name="Yusuf",
    )
    print(response.data)

except InsufficientActionsError as e:
    # Your project does not have this API enabled.
    # Go to the Marketplace and add it.
    print(e.message)

except AuthenticationError as e:
    # Invalid credentials or token fetch failed.
    print(e.message)

except ValidationError as e:
    # Bad input — fix in your code.
    print(e.message)

except APIError as e:
    # The API processed your request but returned an error
    # (e.g. NIN not found, BVN mismatch).
    print(e.message)

except RateLimitError:
    # Too many requests — back off and retry.
    pass

except NetworkError as e:
    # Timeout, connection failure, or server error.
    print(e.message)
```

---

## 7. Enable logging (optional)

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

The SDK logs under `interswitch.auth` and `interswitch.http`. See [Logging](07-logging.md).

---

## Next steps

- [Configuration](01-configuration.md) — all config options, environment variables, Django settings
- [Error Handling](02-error-handling.md) — full exception reference and actions/permissions
- [Async Usage](03-async.md) — `AsyncInterswitchClient` and framework integration
- [API Reference](05-api-reference.md) — every available method
