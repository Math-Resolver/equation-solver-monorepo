from enum import Enum

from pydantic import BaseModel

from api.v1.conversation.schemas.conversation import Conversation

class ConversationHistoryResponse(BaseModel):
    has_recent_conversation: bool
    status: ConversationStatusEnum | None = None
    conversation: Conversation | None = None

class ConversationStatusEnum(str, Enum):
    NO_CONVERSATION_STARTED = "NO_CONVERSATION_STARTED"