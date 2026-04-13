from pydantic import BaseModel

class Conversation(BaseModel):
    id: str
    user_id: str
    messages: list[ConversationMessage]
    started_at: str

class ConversationMessage(BaseModel):
    role: str
    content: str