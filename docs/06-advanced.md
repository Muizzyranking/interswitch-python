# Advanced

---

## Factory method overrides

Both clients use factory methods to create the token manager and HTTP client. Override them in a subclass to inject custom behaviour without touching the wiring.

```python
from interswitch import InterswitchClient
from interswitch.auth.sync_token_manager import TokenManager
from interswitch.http_client.sync_request import SyncRequest
from interswitch.config import Config


class MyClient(InterswitchClient):
    def _create_token_manager(self) -> TokenManager:
        return MyTokenManager(self.config)

    def _create_http_client(self) -> SyncRequest:
        return MyHttpClient(self.config, self.token_manager)
```

The token manager is always created before the HTTP client. The HTTP client always receives `self.token_manager` — so overriding both works correctly without manual wiring.

---

## Custom token manager

Use this if you want to share tokens across multiple processes (e.g. multiple Gunicorn workers) via Redis, Memcached, or any other store.

```python
import json
from datetime import datetime, timedelta
from interswitch.auth.sync_token_manager import TokenManager
from interswitch.config import Config


class RedisTokenManager(TokenManager):
    def __init__(self, config: Config, redis_client):
        super().__init__(config)
        self.redis = redis_client
        self.cache_key = f"isw_token:{config.client_id}"

    def get_token(self) -> str:
        # Check Redis before the in-memory check
        cached = self.redis.get(self.cache_key)
        if cached:
            data = json.loads(cached)
            self._process_new_token_data(data)
            return data["access_token"]
        return super().get_token()

    def get_new_token(self) -> dict:
        data = super().get_new_token()
        ttl = data.get("expires_in", 1799) - 60
        self.redis.setex(self.cache_key, ttl, json.dumps(data))
        return data


class MyClient(InterswitchClient):
    def __init__(self, redis_client, **kwargs):
        self._redis = redis_client
        super().__init__(**kwargs)

    def _create_token_manager(self) -> RedisTokenManager:
        return RedisTokenManager(self.config, self._redis)
```

---

## Custom HTTP client

Use this to add retry logic, circuit breaking, or request/response hooks.

```python
import time
from interswitch.http_client.sync_request import SyncRequest
from interswitch.exceptions import NetworkError


class RetryingHttpClient(SyncRequest):
    def request(self, method, *, endpoint, data=None, params=None, required_scope=None):
        last_error = None
        for attempt in range(3):
            try:
                return super().request(
                    method,
                    endpoint=endpoint,
                    data=data,
                    params=params,
                    required_scope=required_scope,
                )
            except NetworkError as e:
                last_error = e
                time.sleep(2 ** attempt)
        raise last_error


class MyClient(InterswitchClient):
    def _create_http_client(self) -> RetryingHttpClient:
        return RetryingHttpClient(self.config, self.token_manager)
```

---

## Custom config source

Inject credentials from AWS Secrets Manager, HashiCorp Vault, or any other source by subclassing `Config`:

```python
import boto3
import json
from interswitch.config import Config


class SecretsManagerConfig(Config):
    def __init__(self, secret_name: str, region: str = "eu-west-1", **kwargs):
        client = boto3.client("secretsmanager", region_name=region)
        secret = json.loads(client.get_secret_value(SecretId=secret_name)["SecretString"])
        super().__init__(
            client_id=secret["INTERSWITCH_CLIENT_ID"],
            client_secret=secret["INTERSWITCH_CLIENT_SECRET"],
            **kwargs,
        )
```

```python
from interswitch import InterswitchClient

client = InterswitchClient(
    config=SecretsManagerConfig("prod/interswitch")
)
```

---

## Type checking

The package ships a `py.typed` marker file, so mypy and pyright will pick up types automatically. No extra configuration needed.

```python
from interswitch import InterswitchClient
from interswitch.interswitch_types import APIResponse

client: InterswitchClient = InterswitchClient()
response: APIResponse = client.verify_nin(
    nin="12345678901",
    first_name="Muiz",
    last_name="Yusuf",
)
```
