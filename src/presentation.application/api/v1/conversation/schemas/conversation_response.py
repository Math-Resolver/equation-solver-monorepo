from pydantic import BaseModel

class ConversationResponse(BaseModel):
    is_operation_successful: bool
    message: str
    example: str | None = None