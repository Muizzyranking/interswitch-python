# Framework Integration

---

## Django

### Sync client (recommended)

The sync client is the simplest choice for Django. No lifecycle management needed — `requests.Session` handles connection pooling automatically and requires no explicit cleanup.

Configure via `settings.py`:

```python
INTERSWITCH = {
    "CLIENT_ID": env("INTERSWITCH_CLIENT_ID"),
    "CLIENT_SECRET": env("INTERSWITCH_CLIENT_SECRET"),
}
```

Create a module-level client instance — one per process, token cached in memory:

```python
# myapp/services/interswitch.py
from interswitch import InterswitchClient

client = InterswitchClient()
```

Use it in your views:

```python
# myapp/views.py
from django.http import JsonResponse
from interswitch.exceptions import APIError, ValidationError
from interswitch.permissions import InsufficientScopeError
from myapp.services.interswitch import client


def verify_nin_view(request):
    nin = request.POST.get("nin")
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")

    try:
        response = client.verify_nin(
            nin=nin,
            first_name=first_name,
            last_name=last_name,
        )
        return JsonResponse({"data": response.data})

    except ValidationError as e:
        return JsonResponse({"error": e.message}, status=400)

    except APIError as e:
        return JsonResponse({"error": e.message}, status=422)

    except InsufficientScopeError as e:
        return JsonResponse({"error": "API not configured"}, status=503)
```

### Async client in Django

Django supports async views from 3.1+. The async client works fine but the connection pool lives for the process lifetime (Django has no lifespan hook). That is acceptable — `httpx` handles idle timeouts internally.

```python
# myapp/services/interswitch_async.py
from interswitch import AsyncInterswitchClient

client = AsyncInterswitchClient()
```

```python
# myapp/views.py
from django.http import JsonResponse
from myapp.services.interswitch_async import client


async def verify_nin_view(request):
    try:
        response = await client.verify_nin(
            nin=request.POST.get("nin"),
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
        )
        return JsonResponse({"data": response.data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
```

If you want explicit cleanup on process shutdown:

```python
# myapp/apps.py
import atexit
import asyncio
from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = "myapp"

    def ready(self):
        from myapp.services.interswitch_async import client

        def cleanup():
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(client.aclose())
                else:
                    loop.run_until_complete(client.aclose())
            except Exception:
                pass

        atexit.register(cleanup)
```

### Django logging config

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
            "level": "WARNING",   # INFO or DEBUG for development
            "propagate": False,
        },
    },
}
```

---

## FastAPI

FastAPI's dependency injection system is the right place to manage the client lifecycle.

### Sync client via dependency

```python
# app/dependencies.py
from functools import lru_cache
from interswitch import InterswitchClient


@lru_cache
def get_interswitch_client() -> InterswitchClient:
    return InterswitchClient()
```

```python
# app/routes/verification.py
from fastapi import APIRouter, Depends, HTTPException
from interswitch import InterswitchClient
from interswitch.exceptions import APIError, ValidationError
from interswitch.permissions import InsufficientScopeError
from app.dependencies import get_interswitch_client

router = APIRouter()


@router.post("/verify/nin")
def verify_nin(
    nin: str,
    first_name: str,
    last_name: str,
    client: InterswitchClient = Depends(get_interswitch_client),
):
    try:
        response = client.verify_nin(nin=nin, first_name=first_name, last_name=last_name)
        return response.data
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except APIError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except InsufficientScopeError as e:
        raise HTTPException(status_code=503, detail=e.message)
```

### Async client with lifespan

FastAPI's lifespan context manager is the cleanest way to manage the async client — it opens on startup and closes on shutdown:

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from interswitch import AsyncInterswitchClient

interswitch_client: AsyncInterswitchClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global interswitch_client
    interswitch_client = AsyncInterswitchClient()
    yield
    await interswitch_client.aclose()


app = FastAPI(lifespan=lifespan)
```

```python
# app/dependencies.py
from app.main import interswitch_client
from interswitch import AsyncInterswitchClient


def get_interswitch_client() -> AsyncInterswitchClient:
    assert interswitch_client is not None, "Client not initialized"
    return interswitch_client
```

```python
# app/routes/verification.py
from fastapi import APIRouter, Depends, HTTPException
from interswitch import AsyncInterswitchClient
from interswitch.exceptions import APIError, ValidationError
from interswitch.permissions import InsufficientScopeError
from app.dependencies import get_interswitch_client

router = APIRouter()


@router.post("/verify/nin")
async def verify_nin(
    nin: str,
    first_name: str,
    last_name: str,
    client: AsyncInterswitchClient = Depends(get_interswitch_client),
):
    try:
        response = await client.verify_nin(nin=nin, first_name=first_name, last_name=last_name)
        return response.data
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except APIError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except InsufficientScopeError as e:
        raise HTTPException(status_code=503, detail=e.message)
```

### Multiple environments in FastAPI

If you need QA and production clients at the same time (e.g. for testing):

```python
from functools import lru_cache
from interswitch import AsyncInterswitchClient
from app.config import settings


@lru_cache
def get_qa_client() -> AsyncInterswitchClient:
    return AsyncInterswitchClient(
        client_id=settings.INTERSWITCH_QA_CLIENT_ID,
        client_secret=settings.INTERSWITCH_QA_CLIENT_SECRET,
        base_url=settings.INTERSWITCH_QA_BASE_URL,
    )


@lru_cache
def get_prod_client() -> AsyncInterswitchClient:
    return AsyncInterswitchClient(
        client_id=settings.INTERSWITCH_PROD_CLIENT_ID,
        client_secret=settings.INTERSWITCH_PROD_CLIENT_SECRET,
        base_url=settings.INTERSWITCH_PROD_BASE_URL,
    )
```

---

## Flask

### Sync client with application factory

```python
# app/extensions.py
from interswitch import InterswitchClient

interswitch = InterswitchClient()
```

```python
# app/__init__.py
from flask import Flask
from app.extensions import interswitch


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    return app
```

```python
# app/routes/verification.py
from flask import Blueprint, request, jsonify
from interswitch.exceptions import APIError, ValidationError
from interswitch.permissions import InsufficientScopeError
from app.extensions import interswitch

bp = Blueprint("verification", __name__)


@bp.post("/verify/nin")
def verify_nin():
    data = request.get_json()
    try:
        response = interswitch.verify_nin(
            nin=data["nin"],
            first_name=data["first_name"],
            last_name=data["last_name"],
        )
        return jsonify(response.data)
    except ValidationError as e:
        return jsonify({"error": e.message}), 400
    except APIError as e:
        return jsonify({"error": e.message}), 422
    except InsufficientScopeError as e:
        return jsonify({"error": e.message}), 503
```

### Async Flask with Quart

[Quart](https://quart.palletsprojects.com/) is a drop-in async replacement for Flask.

```python
# app/__init__.py
from contextlib import asynccontextmanager
from quart import Quart
from interswitch import AsyncInterswitchClient

interswitch: AsyncInterswitchClient | None = None


def create_app():
    app = Quart(__name__)

    @app.before_serving
    async def startup():
        global interswitch
        interswitch = AsyncInterswitchClient()

    @app.after_serving
    async def shutdown():
        if interswitch:
            await interswitch.aclose()

    return app
```

---

## Celery

For background tasks, create the client at worker startup — not inside the task itself. Creating a new client per task means a new token fetch per task.

```python
# tasks/client.py
from interswitch import InterswitchClient

# Module-level — created once per worker process
client = InterswitchClient()
```

```python
# tasks/verification.py
from celery import shared_task
from interswitch.exceptions import APIError, NetworkError
from tasks.client import client


@shared_task(bind=True, max_retries=3)
def verify_nin_task(self, nin: str, first_name: str, last_name: str) -> dict:
    try:
        response = client.verify_nin(
            nin=nin,
            first_name=first_name,
            last_name=last_name,
        )
        return response.data
    except NetworkError as e:
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
    except APIError as e:
        # Don't retry business errors — return the failure
        return {"error": e.message}
```

---

## General pattern

The same pattern works across all frameworks:

1. Create the client once at application/worker startup, not per request
2. Use the framework's lifecycle hooks to call `close()` / `aclose()` on shutdown
3. The token is cached in memory — no external store needed unless you are running multiple worker processes and want to share tokens across them (see the Redis example in [Advanced](06-advanced.md))
