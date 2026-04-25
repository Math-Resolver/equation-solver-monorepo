import json

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response

from api.v1.dependencies.auth import AuthenticatedUser
from api.v1.dependencies.auth import get_current_user
from api.v1.conversation.schemas import ConversationResponse
from api.v1.conversation.schemas import ConversationRequest
from infrastructure.adapters.cache import CacheService
from infrastructure.adapters.cache import get_cache_service
from infrastructure.adapters.llm_client import AiAdapter
from infrastructure.adapters.llm_client import get_ai_adapter


CACHE_NAMESPACE = "conversation:topic"


router = APIRouter(prefix="/v1", tags=["conversation"])


@router.post("/conversation", response_model=ConversationResponse)
def create_conversation(
    payload: ConversationRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    cache_service: CacheService = Depends(get_cache_service),
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