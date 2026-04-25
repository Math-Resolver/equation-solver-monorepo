from pydantic import BaseModel

class ConversationResponse(BaseModel):
    message: str
    example: str | None = None