from pathlib import Path

from domain.module_loader import load_module_from_path


_ROOT_PATH = Path(__file__).resolve().parents[3]

_CACHE_MODULE = load_module_from_path(
    "infrastructure.data.cache.cache_service",
    _ROOT_PATH / "infrastructure.data" / "cache" / "cache_service.py",
)

RedisCacheService = _CACHE_MODULE.RedisCacheService
get_cache_service = _CACHE_MODULE.get_cache_service

_AI_MODULE = load_module_from_path(
    "infrastructure.adapters.ai.adapters.ai_adapter",
    _ROOT_PATH / "infrastructure.adapters" / "ai" / "adapters" / "ai_adapter.py",
)

AiAdapter = _AI_MODULE.AiAdapter
get_ai_adapter = _AI_MODULE.get_ai_adapter
