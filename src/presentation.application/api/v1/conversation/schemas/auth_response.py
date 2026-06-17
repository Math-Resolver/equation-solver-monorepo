from pydantic import BaseModel, ConfigDict, Field


class RelyingParty(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)


class AuthUser(BaseModel):
    id: str = Field(min_length=1)
    username: str = Field(min_length=1)


class AuthResponse(BaseModel):
    challenge: str = Field(min_length=1)
    relyingParty: RelyingParty
    user: AuthUser

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "challenge": "hallenge-123",
                "relyingParty": {
                    "id": "equation-solver.dev",
                    "name": "Equation Solver"
                },
                "user": {
                    "id": "uuid-123",
                    "username": "user@email.com"
                }
            }
        }
    )