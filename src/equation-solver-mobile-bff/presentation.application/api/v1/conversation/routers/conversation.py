from fastapi import APIRouter, Depends

from api.v1.conversation.repositories.conversation_repository import (
    get_recent_conversation_dep,
)
from api.v1.conversation.schemas.conversation import Conversation
from api.v1.conversation.schemas.conversation_history_response import (
    ConversationHistoryResponse,
    ConversationStatusEnum,
)

router = APIRouter(prefix="/conversation", tags=["conversation"])


@router.get("/history", response_model=ConversationHistoryResponse)
def get_conversation_history(
    conversation: Conversation | None = Depends(get_recent_conversation_dep)
) -> ConversationHistoryResponse:
    if conversation is None:
        return ConversationHistoryResponse(
            has_recent_conversation=False,
            status=ConversationStatusEnum.NO_CONVERSATION_STARTED,
        )

    return ConversationHistoryResponse(
        has_recent_conversation=True,
        conversation=conversation,
    )
