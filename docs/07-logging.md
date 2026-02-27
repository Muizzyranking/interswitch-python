# Logging

The SDK uses Python's standard `logging` module and never configures it. You control everything — handlers, formatters, levels — in your own application.

---

## Logger namespaces

| Logger | What it covers |
|---|---|
| `interswitch.auth` | Token lifecycle — init, fetch, cache hit, refresh, invalidation, errors |
| `interswitch.http` | Every request and response — method, URL, status, timing, retries, errors |

Both are children of `interswitch` so you can control them together or separately.

---

## Quickstart

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Production

Only warnings and errors — no noise, no PII risk:

```python
import logging

logging.getLogger("interswitch").setLevel(logging.WARNING)
```

---

## Development

See every request and token event:

```python
import logging

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    "%(asctime)s %(name)s %(levelname)s %(message)s"
))

logger = logging.getLogger("interswitch")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
```

---

## Granular control

```python
import logging

# Suppress token logs, keep HTTP logs at DEBUG
logging.getLogger("interswitch.auth").setLevel(logging.WARNING)
logging.getLogger("interswitch.http").setLevel(logging.DEBUG)
```

---

## Django

```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "interswitch": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
```

---

## What is and is not logged

**Logged:** HTTP method, URL, status code, response time, error messages, token expiry times, cache hit/miss status.

**Never logged:** Request bodies, response bodies, access tokens, client secrets. The SDK does not log any data that could be PII or a credential.
