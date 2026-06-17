from pydantic import BaseModel, ConfigDict


class AuthFinishResponse(BaseModel):
    status: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok"
            }
        }
    )
