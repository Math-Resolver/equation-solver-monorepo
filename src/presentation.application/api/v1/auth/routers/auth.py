from fastapi import APIRouter

router = APIRouter(prefix="/auth")

@router.post("/resgister/passkey")
def resgister_passkey():
    return {"ok": True}