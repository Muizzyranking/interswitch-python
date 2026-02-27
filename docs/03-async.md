# Async Usage

## Installation

```bash
uv add interswitch-python[async]

# or with pip
pip install interswitch-python[async]
```

This adds `httpx` as a dependency. The sync client uses `requests` and does not require `httpx`.

---

## Basic usage

`AsyncInterswitchClient` has identical methods to `InterswitchClient` — just `await` them.

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
            first_name="Muiz",
            last_name="Yusuf",
        )
        print(response.data)

asyncio.run(main())
```

Use `async with` so the underlying `httpx.AsyncClient` is properly closed when you are done.

---

## Running multiple verifications concurrently

```python
import asyncio
from interswitch import AsyncInterswitchClient

async def main():
    async with AsyncInterswitchClient() as client:
        nin_task = client.verify_nin(
            nin="12345678901", first_name="Muiz", last_name="Yusuf"
        )
        bvn_task = client.verify_bvn_boolean(
            bvn="12345678901", first_name="Muiz", last_name="Yusuf"
        )
        cac_task = client.lookup_cac(company_name="Acme Nigeria")

        nin, bvn, cac = await asyncio.gather(nin_task, bvn_task, cac_task)

        print(nin.data)
        print(bvn.data)
        print(cac.data)

asyncio.run(main())
```

The token is shared across all concurrent calls. The first call fetches it; the rest reuse it. The async lock ensures only one token fetch happens even if ten coroutines hit an expired token at the same time.

---

## Error handling

Identical to sync — same exceptions, same catch order. See [Error Handling](02-error-handling.md).

```python
from interswitch.permissions import InsufficientScopeError
from interswitch.exceptions import APIError, NetworkError

async with AsyncInterswitchClient() as client:
    try:
        response = await client.verify_nin(
            nin="12345678901", first_name="Muiz", last_name="Yusuf"
        )
    except InsufficientScopeError as e:
        print(e.message)
    except APIError as e:
        print(e.message)
    except NetworkError as e:
        print(e.message)
```

---

## Lifecycle

The async client holds an open `httpx.AsyncClient` connection pool. Always close it when done.

Using `async with` is the recommended approach — it calls `aclose()` automatically:

```python
async with AsyncInterswitchClient() as client:
    ...
# connection pool closed here
```

If you manage the client manually (e.g. as a long-lived application singleton), call `aclose()` on shutdown:

```python
client = AsyncInterswitchClient()

# ... use client ...

await client.aclose()
```

For framework-specific lifecycle patterns, see [Framework Integration](04-frameworks.md).

---
