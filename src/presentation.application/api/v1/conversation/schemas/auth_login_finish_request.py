from pydantic import BaseModel, ConfigDict, Field


class AuthLoginFinishRequest(BaseModel):
    email: str = Field(min_length=1)
    credential: str = Field(min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@email.com",
                "credential": "hashASAHASD..."
            }
        }
    )
