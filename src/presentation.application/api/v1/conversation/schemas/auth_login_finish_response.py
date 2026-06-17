from pydantic import BaseModel, ConfigDict, Field


class AuthLoginFinishResponse(BaseModel):
    access_token: str = Field(min_length=1)
    refresh_token: str = Field(min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "access-token",
                "refresh_token": "refresh-token"
            }
        }
    )
