import json
from fastapi import Request
from fastapi.responses import JSONResponse

def _prune_nulls(value):
    if isinstance(value, dict):
        return {key: _prune_nulls(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return [_prune_nulls(item) for item in value]
    return value


async def remove_null_fields_middleware(request: Request, call_next):
    response = await call_next(request)
    content_type = response.headers.get("content-type", "")

    if "application/json" not in content_type:
        return response

    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    payload = json.loads(body.decode("utf-8"))
    cleaned_payload = _prune_nulls(payload)
    headers = {k: v for k, v in response.headers.items() if k.lower() != "content-length"}
    return JSONResponse(
        content=cleaned_payload,
        status_code=response.status_code,
        headers=headers,
    )
