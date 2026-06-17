from pydantic import BaseModel, ConfigDict, Field


class AuthFinishRequest(BaseModel):
    credential: str = Field(min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "credential": "hashASAHASD..."
            }
        }
    )
