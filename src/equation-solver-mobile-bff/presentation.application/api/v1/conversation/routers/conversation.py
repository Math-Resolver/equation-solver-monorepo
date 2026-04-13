from fastapi import APIRouter, Depends, Query

from api.v1.conversation.repositories.conversation_repository import (
    get_past_conversations_dep,
    get_recent_conversation_dep,
)
from api.v1.conversation.schemas.conversation import Conversation
from api.v1.conversation.schemas.conversation_history_response import (
    ConversationHistoryResponse,
    ConversationStatusEnum,
    PastConversationsResponse,
)

router = APIRouter(prefix="/conversation", tags=["conversation"])


@router.get("/active", response_model=ConversationHistoryResponse)
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


@router.get("/history", response_model=PastConversationsResponse)
def get_all_past_conversations(
    conversations: list[Conversation] = Depends(get_past_conversations_dep),
    page: int = Query(1, ge=1),
    limit: int = Query(2, ge=1),
) -> PastConversationsResponse:
    sorted_conversations = sorted(
        conversations,
        key=lambda conversation: conversation.started_at,
        reverse=True,
    )
    total = len(sorted_conversations)
    start = (page - 1) * limit
    end = start + limit

    return PastConversationsResponse(
        conversations=sorted_conversations[start:end],
        page=page,
        limit=limit,
        total=total,
    )
