from fastapi import FastAPI
from api.middlewares.null_pruning import remove_null_fields_middleware
from api.v1.conversation.routers.conversation import router as conversation_router
from api.v1.routers import equations, auth

app = FastAPI()

app.middleware("http")(remove_null_fields_middleware)


app.include_router(equations.router)
app.include_router(auth.router)
app.include_router(conversation_router)