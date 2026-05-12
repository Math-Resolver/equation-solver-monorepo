from pydantic import BaseModel


class TopicsAvailableResponse(BaseModel):
    topics: list[str]