import json
from typing import Any, Optional

from app.config import settings

memory_cache: dict[str, str] = {}


class CacheService:
    def __init__(self):
        self._redis = None

        try:
            from redis import Redis

            self._redis = Redis.from_url(settings.redis_url, decode_responses=True)
            self._redis.ping()
        except Exception:
            self._redis = None

    def get(self, key: str) -> Optional[Any]:
        if not settings.cache_enabled:
            return None

        value = self._get_value(key)
        if value is None:
            return None
        return json.loads(value)

    def set(self, key: str, value: Any, expire_seconds: int = 60) -> None:
        if not settings.cache_enabled:
            return

        text = json.dumps(value, default=str)
        if self._redis is not None:
            self._redis.setex(key, expire_seconds, text)
            return

        memory_cache[key] = text

    def delete_by_prefix(self, prefix: str) -> None:
        if self._redis is not None:
            keys = self._redis.keys(f"{prefix}*")
            if keys:
                self._redis.delete(*keys)
            return

        for key in list(memory_cache.keys()):
            if key.startswith(prefix):
                del memory_cache[key]

    def _get_value(self, key: str) -> Optional[str]:
        if self._redis is not None:
            return self._redis.get(key)
        return memory_cache.get(key)
