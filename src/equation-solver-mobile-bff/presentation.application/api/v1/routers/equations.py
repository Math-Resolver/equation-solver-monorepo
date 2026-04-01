from fastapi import APIRouter

router = APIRouter(prefix="/equations")

@router.post("/solver")
def solver_equation():
    return {"ok": True}