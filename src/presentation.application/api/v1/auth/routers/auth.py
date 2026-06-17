from fastapi import APIRouter, Body

from api.v1.conversation.schemas.auth_finish_request import AuthFinishRequest
from api.v1.conversation.schemas.auth_finish_response import AuthFinishResponse
from api.v1.conversation.schemas.auth_login_finish_request import AuthLoginFinishRequest
from api.v1.conversation.schemas.auth_login_finish_response import AuthLoginFinishResponse
from api.v1.conversation.schemas.auth_login_request import AuthLoginRequest
from api.v1.conversation.schemas.auth_refresh_token_request import AuthRefreshTokenRequest
from api.v1.conversation.schemas.auth_request import AuthRequest
from api.v1.conversation.schemas.auth_response import AuthUser
from api.v1.conversation.schemas.auth_response import AuthResponse
from api.v1.conversation.schemas.auth_response import RelyingParty

router = APIRouter(prefix="/v1/auth", tags=["auth"])

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
    payload: AuthRequest = Body(
        ...,
        example={
        "displayName": "user@gmail.com",
        "deviceFingerprint": "iphone-15,5/uuid"
        }
  )
) -> AuthResponse:
  return AuthResponse(
    challenge="hashASAHASD...",
    relyingParty=RelyingParty(id="seuapp.com", name="Seu App"),
    user=AuthUser(id="uuid-123", username=payload.displayName)
  )


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
  payload: AuthFinishRequest = Body(
    ...,
    example={
      "credential": "hashASAHASD..."
    }
  )
) -> AuthFinishResponse:
  _ = payload
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
  payload: AuthLoginRequest = Body(
    ...,
    example={
      "email": "user@gmail.com"
    }
  )
) -> AuthResponse:
  return AuthResponse(
    challenge="hashASJANS...",
    relyingParty=RelyingParty(id="seuapp.com", name="Seu App"),
    user=AuthUser(id="uuid-123", username=payload.email)
  )


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
  payload: AuthLoginFinishRequest = Body(
    ...,
    example={
      "credential": "hashASAHASD..."
    }
  )
) -> AuthLoginFinishResponse:
  _ = payload
  return AuthLoginFinishResponse(
    access_token="access-token",
    refresh_token="refresh-token"
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
  payload: AuthRefreshTokenRequest = Body(
    ...,
    example={
      "token": "hashASAHASD..."
    }
  )
) -> AuthLoginFinishResponse:
  _ = payload
  return AuthLoginFinishResponse(
    access_token="access-token",
    refresh_token="refresh-token"
  )
