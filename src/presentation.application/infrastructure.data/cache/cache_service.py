import logging
import os
from hashlib import sha256
from typing import Any
from domain.abstractions import CacheServiceAbstraction
from redis import Redis

logger = logging.getLogger(__name__)


DEFAULT_CACHE_TTL_SECONDS = 3600

class RedisCacheService(CacheServiceAbstraction):
    def __init__(self, redis_client: Any, default_ttl_seconds: int):
        self._redis_client = redis_client
        self._default_ttl_seconds = default_ttl_seconds

    def read_json_entry(self, namespace: str, key: str) -> str | None:
        try:
            cache_key = _build_cache_key(namespace, key)
            cached_payload = self._redis_client.get(cache_key)
        except Exception as exc:
            logger.warning("Failed to read cache entry", exc_info=exc)
            return None
        if cached_payload is None:
            return None
        return cached_payload

    def write_json_entry(self, namespace: str, key: str, value: str, ttl_seconds: int | None = None) -> None:
        effective_ttl = ttl_seconds or self._default_ttl_seconds
        try:
            cache_key = _build_cache_key(namespace, key)
            self._redis_client.setex(cache_key, effective_ttl, value)
        except Exception as exc:
            logger.warning("Failed to write cache entry", exc_info=exc)
            return


def get_cache_service() -> CacheService:
    redis_url = os.getenv("REDIS_URL")
    ttl_seconds = int(
        os.getenv("CACHE_DEFAULT_TTL_SECONDS",os.getenv("CONVERSATION_CACHE_TTL_SECONDS", str(DEFAULT_CACHE_TTL_SECONDS)))
    )
    redis_client = Redis.from_url(redis_url, decode_responses=True)
    return RedisCacheService(redis_client=redis_client, default_ttl_seconds=ttl_seconds)


def _build_cache_key(namespace: str, key: str) -> str:
    normalized_key = key.strip().lower()
    key_hash = sha256(normalized_key.encode("utf-8")).hexdigest()
    return f"{namespace}:{key_hash}"