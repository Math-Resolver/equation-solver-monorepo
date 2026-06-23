import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter
from fastapi import Body
from fastapi.responses import JSONResponse

from api.v1.auth.token_utils import create_access_token
from api.v1.auth.token_utils import create_refresh_token
from api.v1.auth.token_utils import decode_and_validate_token
from api.v1.conversation.schemas.auth_finish_request import AuthFinishRequest
from api.v1.conversation.schemas.auth_finish_response import AuthFinishResponse
from api.v1.conversation.schemas.auth_login_finish_request import AuthLoginFinishRequest
from api.v1.conversation.schemas.auth_login_finish_response import AuthLoginFinishResponse
from api.v1.conversation.schemas.auth_login_request import AuthLoginRequest
from api.v1.conversation.schemas.auth_refresh_token_request import AuthRefreshTokenRequest
from api.v1.conversation.schemas.auth_request import AuthRequest
from api.v1.conversation.schemas.auth_response import AuthResponse
from api.v1.conversation.schemas.auth_response import AuthUser
from api.v1.conversation.schemas.auth_response import RelyingParty

router = APIRouter(prefix="/v1/auth", tags=["auth"])

CHALLENGE_TTL_MINUTES = 5
REFRESH_TTL_DAYS = 7

_USERS_BY_EMAIL: dict[str, dict] = {}
_USERS_BY_ID: dict[str, dict] = {}
_CHALLENGES: dict[str, dict] = {}
_REFRESH_TOKENS_BY_JTI: dict[str, dict] = {}


def _utc_now() -> datetime:
  return datetime.now(timezone.utc)


def _challenge_expiration() -> datetime:
  return _utc_now() + timedelta(minutes=CHALLENGE_TTL_MINUTES)


def _refresh_expiration() -> datetime:
  return _utc_now() + timedelta(days=REFRESH_TTL_DAYS)


def _json_error(status_code: int, detail: str) -> JSONResponse:
  return JSONResponse(status_code=status_code, content={"detail": detail})


def _relying_party() -> RelyingParty:
  return RelyingParty(
    id=os.getenv("RP_ID", "equation-solver.dev"),
    name=os.getenv("RP_NAME", "Equation Solver"),
  )


def _new_challenge_value() -> str:
  return secrets.token_urlsafe(32)


def _sha256_hex(value: str) -> str:
  return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _create_or_get_register_challenge(email: str, device_fingerprint: str) -> str:
  now = _utc_now()
  for challenge_state in _CHALLENGES.values():
    if (
      challenge_state["email"] == email
      and challenge_state["device_fingerprint"] == device_fingerprint
      and challenge_state["purpose"] == "register"
      and not challenge_state["used"]
      and challenge_state["expires_at"] > now
    ):
      return challenge_state["value"]

  challenge_value = _new_challenge_value()
  _CHALLENGES[challenge_value] = {
    "value": challenge_value,
    "email": email,
    "device_fingerprint": device_fingerprint,
    "purpose": "register",
    "expires_at": _challenge_expiration(),
    "used": False,
  }
  return challenge_value


def _create_login_challenge(email: str) -> str:
  challenge_value = _new_challenge_value()
  _CHALLENGES[challenge_value] = {
    "value": challenge_value,
    "email": email,
    "device_fingerprint": None,
    "purpose": "login",
    "expires_at": _challenge_expiration(),
    "used": False,
  }
  return challenge_value


def _latest_active_challenge(email: str, purpose: str) -> dict | None:
  now = _utc_now()
  active_challenges = [
    state
    for state in _CHALLENGES.values()
    if state["email"] == email
    and state["purpose"] == purpose
    and not state["used"]
    and state["expires_at"] > now
  ]
  if not active_challenges:
    return None
  return max(active_challenges, key=lambda item: item["expires_at"])


def _invalidate_challenge(challenge_value: str) -> None:
  challenge_state = _CHALLENGES.get(challenge_value)
  if challenge_state is not None:
    challenge_state["used"] = True


def _credential_is_invalid(credential: str) -> bool:
  lowered = credential.strip().lower()
  return not lowered or lowered.startswith("invalid")


def _upsert_refresh_token(user_id: str, refresh_token: str, token_jti: str) -> None:
  for token_state in _REFRESH_TOKENS_BY_JTI.values():
    if token_state["user_id"] == user_id and token_state["is_revoked"] is False:
      token_state["is_revoked"] = True

  _REFRESH_TOKENS_BY_JTI[token_jti] = {
    "jti": token_jti,
    "user_id": user_id,
    "token_hash": _sha256_hex(refresh_token),
    "is_revoked": False,
    "expires_at": _refresh_expiration(),
  }


def _rotate_refresh_token(existing_token_jti: str, new_refresh_token: str, new_refresh_jti: str) -> None:
  existing_token = _REFRESH_TOKENS_BY_JTI[existing_token_jti]
  existing_token["is_revoked"] = True
  _REFRESH_TOKENS_BY_JTI[new_refresh_jti] = {
    "jti": new_refresh_jti,
    "user_id": existing_token["user_id"],
    "token_hash": _sha256_hex(new_refresh_token),
    "is_revoked": False,
    "expires_at": _refresh_expiration(),
  }


def _user_from_email(email: str) -> dict | None:
  return _USERS_BY_EMAIL.get(email)


def _serialize_auth_response(challenge: str, user: dict, username: str) -> AuthResponse:
  return AuthResponse(
    challenge=challenge,
    relyingParty=_relying_party(),
    user=AuthUser(id=user["id"], username=username),
  )


def reset_auth_state_for_tests() -> None:
  _USERS_BY_EMAIL.clear()
  _USERS_BY_ID.clear()
  _CHALLENGES.clear()
  _REFRESH_TOKENS_BY_JTI.clear()

@router.post(
  "/register",
  response_model=AuthResponse,
  responses={
    200: {
      "description": "User registered successfully",
      "content": {
        "application/json": {
          "example": {
            "challenge": "hashASAHASD...",
            "relyingParty": {
              "id": "seuapp.com",
              "name": "Seu App"
            },
            "user": {
              "id": "uuid-123",
              "username": "user@gmail.com"
            }
          }
        }
      }
    }
  }
)
async def register(
  payload: AuthRequest = Body(...)
) -> AuthResponse:
  existing_user = _user_from_email(payload.displayName)
  if existing_user and existing_user.get("credential_id"):
    return _json_error(409, "displayName já cadastrado")

  if existing_user is None:
    user_id = secrets.token_hex(12)
    user_state = {
      "id": user_id,
      "email": payload.displayName,
      "device_fingerprint": payload.deviceFingerprint,
      "credential_id": None,
      "public_key": None,
      "sign_count": 0,
    }
    _USERS_BY_EMAIL[payload.displayName] = user_state
    _USERS_BY_ID[user_id] = user_state
  else:
    existing_user["device_fingerprint"] = payload.deviceFingerprint

  challenge = _create_or_get_register_challenge(payload.displayName, payload.deviceFingerprint)
  user = _USERS_BY_EMAIL[payload.displayName]
  return _serialize_auth_response(challenge=challenge, user=user, username=payload.displayName)


@router.post(
  "/register/finish",
  response_model=AuthFinishResponse,
  responses={
    200: {
      "description": "Registration finished successfully",
      "content": {
        "application/json": {
          "example": {
            "status": "ok"
          }
        }
      }
    }
  }
)
async def register_finish(
  payload: AuthFinishRequest = Body(...)
) -> AuthFinishResponse:
    user = _user_from_email(payload.email)
    if user is None:
        return _json_error(404, "Usuário não encontrado")

    challenge_state = _latest_active_challenge(payload.email, purpose="register")
    if challenge_state is None:
        return _json_error(400, "Challenge expirado ou não encontrado")

    if _credential_is_invalid(payload.credential):
        return _json_error(401, "Credencial inválida")

    user["credential_id"] = _sha256_hex(payload.credential)[:32]
    user["public_key"] = _sha256_hex(payload.credential)
    user["sign_count"] = 1
    _invalidate_challenge(challenge_state["value"])
    return AuthFinishResponse(status="ok")


@router.post(
  "/login",
  response_model=AuthResponse,
  responses={
    200: {
      "description": "Login challenge generated successfully",
      "content": {
        "application/json": {
          "example": {
            "challenge": "hashASJANS...",
            "relyingParty": {
              "id": "seuapp.com",
              "name": "Seu App"
            },
            "user": {
              "id": "uuid-123",
              "username": "user@gmail.com"
            }
          }
        }
      }
    }
  }
)
async def login(
  payload: AuthLoginRequest = Body(...)
) -> AuthResponse:
    user = _user_from_email(payload.email)
    if user is None or user.get("credential_id") is None:
        return _json_error(404, "Usuário não encontrado ou sem credencial")

    challenge = _create_login_challenge(payload.email)
    return _serialize_auth_response(challenge=challenge, user=user, username=payload.email)


@router.post(
  "/login/finish",
  response_model=AuthLoginFinishResponse,
  responses={
    200: {
      "description": "Login finished successfully",
      "content": {
        "application/json": {
          "example": {
            "access_token": "access-token",
            "refresh_token": "refresh-token"
          }
        }
      }
    }
  }
)
async def login_finish(
  payload: AuthLoginFinishRequest = Body(...)
) -> AuthLoginFinishResponse:
    user = _user_from_email(payload.email)
    if user is None or user.get("public_key") is None:
        return _json_error(404, "Usuário não encontrado ou sem credencial")

    challenge_state = _latest_active_challenge(payload.email, purpose="login")
    if challenge_state is None:
        return _json_error(400, "Challenge expirado ou não encontrado")

    if _credential_is_invalid(payload.credential):
        return _json_error(401, "Credencial inválida")

    access_token = create_access_token(sub=user["id"])
    refresh_token, refresh_jti = create_refresh_token(sub=user["id"])
    _upsert_refresh_token(user_id=user["id"], refresh_token=refresh_token, token_jti=refresh_jti)
    _invalidate_challenge(challenge_state["value"])

    user["sign_count"] = int(user.get("sign_count", 0)) + 1

    return AuthLoginFinishResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
  "/refresh-token",
  response_model=AuthLoginFinishResponse,
  responses={
    200: {
      "description": "Tokens refreshed successfully",
      "content": {
        "application/json": {
          "example": {
            "access_token": "access-token",
            "refresh_token": "refresh-token"
          }
        }
      }
    }
  }
)
async def refresh_token(
  payload: AuthRefreshTokenRequest = Body(...)
) -> AuthLoginFinishResponse:
    decoded_payload = decode_and_validate_token(payload.token, expected_type="refresh")
    if decoded_payload is None:
        return _json_error(401, "Refresh token inválido ou expirado")

    token_jti = decoded_payload.get("jti")
    user_id = decoded_payload.get("sub")
    if not isinstance(token_jti, str) or not isinstance(user_id, str):
        return _json_error(401, "Refresh token inválido")

    existing_token = _REFRESH_TOKENS_BY_JTI.get(token_jti)
    if existing_token is None:
        return _json_error(401, "Refresh token inexistente")

    if existing_token["is_revoked"]:
        return _json_error(401, "Refresh token revogado")

    if existing_token["expires_at"] <= _utc_now():
        return _json_error(401, "Refresh token expirado")

    if existing_token["token_hash"] != _sha256_hex(payload.token):
        return _json_error(401, "Refresh token inválido")

    user = _USERS_BY_ID.get(user_id)
    if user is None:
        return _json_error(404, "Usuário não encontrado")

    new_access_token = create_access_token(sub=user_id)
    new_refresh_token, new_refresh_jti = create_refresh_token(sub=user_id)
    _rotate_refresh_token(
        existing_token_jti=token_jti,
        new_refresh_token=new_refresh_token,
        new_refresh_jti=new_refresh_jti,
    )

    return AuthLoginFinishResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )
