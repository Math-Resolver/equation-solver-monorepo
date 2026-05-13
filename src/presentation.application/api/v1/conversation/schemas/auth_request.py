from pydantic import BaseModel

class RegisterRequest(BaseModel):
    displayName: str
    deviceFingerprint: str