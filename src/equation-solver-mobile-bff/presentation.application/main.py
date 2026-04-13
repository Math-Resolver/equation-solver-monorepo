from fastapi import FastAPI
from api.v1.conversation.routers.conversation import router as conversation_router
from api.v1.routers import equations, auth

app = FastAPI()

app.include_router(equations.router)
app.include_router(auth.router)
app.include_router(conversation_router)