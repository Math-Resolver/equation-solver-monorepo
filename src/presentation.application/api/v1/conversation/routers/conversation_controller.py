import json

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi.responses import JSONResponse

from api.v1.dependencies.auth import AuthenticatedUser
from api.v1.dependencies.auth import get_current_user
from api.v1.dependencies.service_injection import AiAdapter
from api.v1.dependencies.service_injection import RedisCacheService
from api.v1.dependencies.service_injection import get_ai_adapter
from api.v1.dependencies.service_injection import get_cache_service
from api.v1.conversation.schemas.conversation_request import ConversationRequest
from api.v1.conversation.schemas.conversation_response import ConversationResponse


CACHE_NAMESPACE = "conversation:topic"


router = APIRouter(prefix="/v1", tags=["conversation"])


@router.post(
        "/conversation", 
        response_model=ConversationResponse,
        responses={
            200: {
                "description": "Conversation generated successfully"
            },
            401: {
                "description": "Unauthorized"
            },
            502: {
                "description": "AI provider unavailable or failed to generate response",
                "content": {
                    "application/json": {
                        "example": {
                            "is_operation_successful": False,
                            "message": "AI provider unavailable or failed to generate response",
                            "example": None
                        }
                    }
                }
            }
        })
def create_conversation(
    payload: ConversationRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    cache_service: RedisCacheService = Depends(get_cache_service),
    ai_adapter: AiAdapter = Depends(get_ai_adapter)
):
    _ = current_user
    cached_response = cache_service.read_json_entry(CACHE_NAMESPACE, payload.topic)
    if cached_response is not None:
        return build_response_with_error_handling(ConversationResponse(**json.loads(cached_response)))
    explanation = ai_adapter.retrieve_explanation(payload.topic)
    conversation_response = ConversationResponse(is_operation_successful=explanation.is_operation_successful, message=explanation.message, example=explanation.example)
    if not conversation_response.is_operation_successful:
        return build_response_with_error_handling(conversation_response)
    cache_service.write_json_entry(CACHE_NAMESPACE, payload.topic, _serialize_response(conversation_response))
    return conversation_response


def _serialize_response(response: ConversationResponse) -> str:
    if hasattr(response, "model_dump"):
        return json.dumps(response.model_dump())
    return json.dumps(response.model())


def build_response_with_error_handling(response: ConversationResponse) -> ConversationResponse | JSONResponse:
    if not response.is_operation_successful:
        return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content=response.model_dump())
    return response