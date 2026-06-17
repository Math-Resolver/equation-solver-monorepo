import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
	sys.path.insert(0, str(_ROOT))

from fastapi import FastAPI
from api.middlewares.null_pruning import remove_null_fields_middleware
from api.v1.auth.routers import auth
from api.v1.conversation.routers import conversation_controller
from api.v1.equations.routers import equations

app = FastAPI()

app.middleware("http")(remove_null_fields_middleware)


@app.get("/v1/health", tags=["system"])
def health_check():
	return {"status": "ok"}


app.include_router(equations.router)
app.include_router(auth.router)
app.include_router(conversation_controller.router)
