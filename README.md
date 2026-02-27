# interswitch-python

Python SDK for the [Interswitch Identity API](https://developer.interswitchgroup.com/).

Supports Python 3.10+. Both sync and async clients. Zero required dependencies beyond `requests`.

---

## Installation

```bash
uv add interswitch-python

# with pip
pip install interswitch-python
```

For async support:

```bash
uv add interswitch-python[async]

# with pip
pip install interswitch-python[async]
```

---

## Quick start

```python
from interswitch import InterswitchClient

client = InterswitchClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
)

response = client.verify_nin(
    nin="12345678901",
    first_name="Muiz",
    last_name="Yusuf",
)
print(response.data)
```

### Async:

```python
import asyncio
from interswitch import AsyncInterswitchClient

async def main():
    async with AsyncInterswitchClient(
        client_id="your-client-id",
        client_secret="your-client-secret",
    ) as client:
        response = await client.verify_bvn_boolean(
            bvn="12345678901",
            first_name="Muiz",
            last_name="Yusuf",
        )
        print(response.data)

asyncio.run(main())
```

---

## Credentials

Go to [developer.interswitchgroup.com](https://developer.interswitchgroup.com/), create a project, and select the APIs you need. Each project gives you a Client ID and Client Secret scoped to those APIs.

You can pass credentials directly, use environment variables, or configure them via Django settings.

```bash
export INTERSWITCH_CLIENT_ID=your-client-id
export INTERSWITCH_CLIENT_SECRET=your-client-secret
```

---

## Documentation

- [Getting Started](docs/00-getting-started.md)
- [Configuration](docs/01-configuration.md)
- [Error Handling](docs/02-error-handling.md)
- [Async Usage](docs/03-async.md)
- [Framework Integration](docs/04-frameworks.md)
- [API Reference](docs/05-api-reference.md)
- [Advanced](docs/06-advanced.md)
- [Logging](docs/07-logging.md)

---

## License

MIT
