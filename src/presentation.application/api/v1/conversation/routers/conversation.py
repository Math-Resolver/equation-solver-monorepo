import json
import sys
from importlib.util import module_from_spec
from importlib.util import spec_from_file_location
from pathlib import Path

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response

from api.v1.dependencies.auth import AuthenticatedUser
from api.v1.dependencies.auth import get_current_user
from api.v1.conversation.schemas.conversation_request import ConversationRequest
from api.v1.conversation.schemas.conversation_response import ConversationResponse


_ROOT_PATH = Path(__file__).resolve().parents[4]

_CACHE_MODULE_PATH = _ROOT_PATH / "infrastructure.data" / "cache" / "cache_service.py"
_CACHE_MODULE_SPEC = spec_from_file_location("infrastructure.data.cache.cache_service", _CACHE_MODULE_PATH)
_CACHE_MODULE = module_from_spec(_CACHE_MODULE_SPEC)
assert _CACHE_MODULE_SPEC is not None
assert _CACHE_MODULE_SPEC.loader is not None
sys.modules[_CACHE_MODULE_SPEC.name] = _CACHE_MODULE
_CACHE_MODULE_SPEC.loader.exec_module(_CACHE_MODULE)

RedisCacheService = _CACHE_MODULE.RedisCacheService
get_cache_service = _CACHE_MODULE.get_cache_service


_AI_MODULE_PATH = _ROOT_PATH / "infrastructure.adapters" / "ai" / "adapters" / "ai_adapter.py"
_AI_MODULE_SPEC = spec_from_file_location("infrastructure.adapters.ai.adapters.ai_adapter", _AI_MODULE_PATH)
_AI_MODULE = module_from_spec(_AI_MODULE_SPEC)
assert _AI_MODULE_SPEC is not None
assert _AI_MODULE_SPEC.loader is not None
sys.modules[_AI_MODULE_SPEC.name] = _AI_MODULE
_AI_MODULE_SPEC.loader.exec_module(_AI_MODULE)

AiAdapter = _AI_MODULE.AiAdapter
get_ai_adapter = _AI_MODULE.get_ai_adapter


CACHE_NAMESPACE = "conversation:topic"


router = APIRouter(prefix="/v1", tags=["conversation"])


@router.post("/conversation", response_model=ConversationResponse)
def create_conversation(
    payload: ConversationRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    cache_service: RedisCacheService = Depends(get_cache_service),
    ai_adapter: AiAdapter = Depends(get_ai_adapter)
):
    _ = current_user
    cached_response = cache_service.read_json_entry(CACHE_NAMESPACE, payload.topic)
    if cached_response is not None:
        return ConversationResponse(**json.loads(cached_response))
    explanation = ai_adapter.retrieve_explanation(payload.topic)
    conversation_response = ConversationResponse(message=explanation.message, example=explanation.example)
    cache_service.write_json_entry(CACHE_NAMESPACE, payload.topic, _serialize_response(conversation_response))
    return conversation_response


def _serialize_response(response: ConversationResponse) -> str:
    if hasattr(response, "model_dump"):
        return json.dumps(response.model_dump())
    return json.dumps(response.dict())