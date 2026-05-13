from pydantic import BaseModel

class UserData(BaseModel):
    id: str
    displayName: str

class RegisterResponse(BaseModel):
    challenge: str
    relyingParty: str
    user: UserData