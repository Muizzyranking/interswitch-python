# Error Handling

## Contract

If a method returns, the response is always successful. You never need to check `response.success` — if something went wrong, an exception was raised instead. This means your happy path is always clean:

```python
response = client.verify_nin(nin="12345678901", first_name="Muiz", last_name="Yusuf")
print(response.data)  # safe — if we got here, it worked
```

---

## Exception hierarchy

```
Exception
└── InsufficientScopeError          # project not configured for this API

InterswitchError (base)
├── AuthenticationError             # token fetch failed / bad credentials
├── APIError                        # API returned a business-level error
│   ├── ValidationError             # bad input (400)
│   └── RateLimitError              # too many requests (429)
├── NetworkError                    # timeout, connection failure, 5xx
└── ConfigurationError              # missing credentials or bad config
```

`InsufficientScopeError` sits outside `InterswitchError` because it is a configuration problem, not an API error.

---

## InsufficientScopeError

Raised when your token does not include the scope required to call a method. The check happens after the token is fetched — so it works correctly on the first call.

```python
from interswitch.permissions import InsufficientScopeError

try:
    response = client.lookup_cac(company_name="Acme")
except InsufficientScopeError as e:
    print(e.message)
    # "Your token does not have permission for this API.
    #  Required: 'MonoCac'. Go to the Interswitch Marketplace,
    #  open your project, and enable the missing API product."

    print(e.required_scope)      # ['MonoCac']
    print(e.available_actions)   # what your token actually has
```

**Fix:** Go to the Interswitch Marketplace, open your project, and enable the API product that corresponds to the required scope. Re-generate your credentials or wait for the current token to expire.

Every method documents its required scope in the [API Reference](05-api-reference.md). You can also check what your current token has access to:

```python
info = client.get_token_info()
print(info["api_actions"])
# ['VerifyMeNin', 'VerifyMeBvn', 'MonoCac', ...]
```

---

## AuthenticationError

Token fetch failed. Usually means bad credentials or the token URL is wrong.

```python
from interswitch.exceptions import AuthenticationError

try:
    response = client.verify_nin(...)
except AuthenticationError as e:
    print(e.message)
    print(e.response_data)  # raw response from the token endpoint, if available
```

The SDK retries once automatically on a 401 response mid-session (token expired unexpectedly). If the retry also fails, `AuthenticationError` is raised.

---

## ValidationError

Raised on HTTP 400. Your request was malformed — wrong format, missing field, value out of range.

```python
from interswitch.exceptions import ValidationError

try:
    response = client.verify_bvn_boolean(bvn="123", first_name="Muiz", last_name="Yusuf")
except ValidationError as e:
    print(e.message)       # "BVN must be 11 digits"
    print(e.status_code)   # "400"
    print(e.response_data) # full error body from the API
```

---

## APIError

Raised when the API processed your request but returned an error result — NIN not found, BVN mismatch, record not available, etc.

```python
from interswitch.exceptions import APIError

try:
    response = client.verify_nin(nin="00000000000", first_name="Muiz", last_name="Yusuf")
except APIError as e:
    print(e.message)       # "NIN not found. Provide a valid NIN"
    print(e.status_code)   # "ERROR"
    print(e.response_data) # full response body
```

---

## RateLimitError

Raised on HTTP 429. Back off and retry.

```python
from interswitch.exceptions import RateLimitError
import time

for attempt in range(3):
    try:
        response = client.verify_nin(...)
        break
    except RateLimitError:
        time.sleep(2 ** attempt)  # exponential backoff
```

---

## NetworkError

Raised on timeout, connection failure, or 5xx server error.

```python
from interswitch.exceptions import NetworkError

try:
    response = client.verify_nin(...)
except NetworkError as e:
    print(e.message)   # "Request timed out" / "Connection failed" / "Server error occurred"
    print(e.reason)    # more detail
```

---

## ConfigurationError

Raised when credentials are missing or invalid at initialization time.

```python
from interswitch.exceptions import ConfigurationError

try:
    client = InterswitchClient()
    response = client.verify_nin(...)
except ConfigurationError as e:
    print(e.message)
    # "Client ID not found. Set INTERSWITCH_CLIENT_ID or pass client_id=..."
```

---

## Recommended catch order

```python
from interswitch.permissions import InsufficientScopeError
from interswitch.exceptions import (
    AuthenticationError,
    ValidationError,
    APIError,
    RateLimitError,
    NetworkError,
    InterswitchError,
)

try:
    response = client.verify_nin(...)

except InsufficientScopeError as e:
    # Project config problem — fix in the Marketplace
    log.error("API not enabled: %s", e.required_scope)

except AuthenticationError as e:
    # Credentials problem — check config
    log.error("Auth failed: %s", e.message)

except ValidationError as e:
    # Bad input — fix in code
    log.warning("Invalid request: %s", e.message)

except APIError as e:
    # Business-level failure — handle in logic
    log.info("Verification failed: %s", e.message)

except RateLimitError:
    # Infrastructure — retry with backoff
    pass

except NetworkError as e:
    # Infrastructure — retry or alert
    log.error("Network error: %s", e.message)

except InterswitchError as e:
    # Catch-all for anything else from the SDK
    log.error("SDK error: %s", e.message)
```
