from pydantic import BaseModel
from pydantic import constr


class ConversationRequest(BaseModel):
    topic: constr(strip_whitespace=True, min_length=1)