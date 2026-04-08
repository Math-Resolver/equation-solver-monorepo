from fastapi import FastAPI

from api.v1.routers.equations import router as equations_router
from api.v1.routers.auth import router as auth_router

app = FastAPI(title="Equation Solver Mobile BFF", version="1.0.0")
app.include_router(equations_router)
app.include_router(auth_router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
