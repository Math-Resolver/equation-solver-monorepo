from pydantic import BaseModel, ConfigDict, Field


class AuthRequest(BaseModel):
    displayName: str = Field(min_length=1)
    deviceFingerprint: str = Field(min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "displayName": "user@gmail.com",
                "deviceFingerprint": "iphone-15,5/uuid"
            }
        }
    )