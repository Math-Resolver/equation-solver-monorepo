from fastapi import APIRouter, status

router = APIRouter(prefix="/auth")

@router.post("/register/passkey")
def resgister_passkey():
    return {"ok": True}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register():
    return {"message": "Iniciando registro na estrutura nova"}