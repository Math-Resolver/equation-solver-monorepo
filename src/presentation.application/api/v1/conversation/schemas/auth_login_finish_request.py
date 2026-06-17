from pydantic import BaseModel, ConfigDict, Field


class AuthLoginFinishRequest(BaseModel):
    credential: str = Field(min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "credential": "hashASAHASD..."
            }
        }
    )
