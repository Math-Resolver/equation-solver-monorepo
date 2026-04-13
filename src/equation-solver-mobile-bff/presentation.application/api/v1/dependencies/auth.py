import base64
import json
import time

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

security = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    user_id: str
    token: str


def _decode_jwt_payload(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=401, detail="Invalid JWT token.")

    padding = "=" * (-len(parts[1]) % 4)
    try:
        payload = json.loads(
            base64.urlsafe_b64decode((parts[1] + padding).encode()).decode()
        )
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=401, detail="Invalid JWT token.") from exc

    if not isinstance(payload, dict):
        raise HTTPException(status_code=401, detail="Invalid JWT token.")

    exp = payload.get("exp")
    if isinstance(exp, (int, float)) and exp < time.time():
        raise HTTPException(status_code=401, detail="Token expired.")

    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(status_code=401, detail="User not authenticated.")

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme.")

    token = credentials.credentials.strip()
    if not token:
        raise HTTPException(status_code=401, detail="User not authenticated.")

    payload = _decode_jwt_payload(token)
    user_id = str(
        payload.get("sub") or payload.get("user_id") or "authenticated-user"
    )

    return AuthenticatedUser(user_id=user_id, token=token)
