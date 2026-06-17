from pydantic import BaseModel, ConfigDict, Field


class AuthLoginRequest(BaseModel):
    email: str = Field(min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@email.com"
            }
        }
    )
