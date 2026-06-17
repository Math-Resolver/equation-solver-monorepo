from pydantic import BaseModel, ConfigDict, Field


class AuthRefreshTokenRequest(BaseModel):
    token: str = Field(min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "hashASAHASD..."
            }
        }
    )
