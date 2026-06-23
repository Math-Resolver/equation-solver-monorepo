import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def _utc_now_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def _jwt_secret() -> str:
    return os.getenv("AUTH_SECRET_KEY") or os.getenv("SECRET_KEY") or "dev-auth-secret"


def _sign_signing_input(signing_input: str, secret: str) -> str:
    signature = hmac.new(
        secret.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return _b64url_encode(signature)


def create_token(sub: str, token_type: str, lifetime: timedelta, jti: str | None = None) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now_ts = _utc_now_ts()
    payload: dict[str, Any] = {
        "sub": sub,
        "type": token_type,
        "iat": now_ts,
        "exp": now_ts + int(lifetime.total_seconds()),
    }
    if jti is not None:
        payload["jti"] = jti

    encoded_header = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_payload}"
    signature = _sign_signing_input(signing_input, _jwt_secret())
    return f"{signing_input}.{signature}"


def create_access_token(sub: str) -> str:
    return create_token(sub=sub, token_type="access", lifetime=timedelta(minutes=15))


def create_refresh_token(sub: str) -> tuple[str, str]:
    jti = str(uuid4())
    token = create_token(sub=sub, token_type="refresh", lifetime=timedelta(days=7), jti=jti)
    return token, jti


def decode_and_validate_token(token: str, expected_type: str | None = None) -> dict[str, Any] | None:
    parts = token.split(".")
    if len(parts) != 3:
        return None

    encoded_header, encoded_payload, signature = parts
    signing_input = f"{encoded_header}.{encoded_payload}"
    expected_signature = _sign_signing_input(signing_input, _jwt_secret())
    if not hmac.compare_digest(signature, expected_signature):
        return None

    try:
        payload = json.loads(_b64url_decode(encoded_payload).decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        return None

    if not isinstance(payload, dict):
        return None

    exp = payload.get("exp")
    sub = payload.get("sub")
    if not isinstance(exp, int) or not isinstance(sub, str) or not sub:
        return None
    if _utc_now_ts() >= exp:
        return None

    token_type = payload.get("type")
    if expected_type is not None and token_type != expected_type:
        return None

    return payload