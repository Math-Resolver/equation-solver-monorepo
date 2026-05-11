from fastapi import FastAPI
from api.middlewares.null_pruning import remove_null_fields_middleware
from api.v1.auth.routers import auth
from api.v1.conversation.routers import conversation_controller
from api.v1.equations.routers import equations

app = FastAPI()

app.middleware("http")(remove_null_fields_middleware)


app.include_router(equations.router)
app.include_router(auth.router)
app.include_router(conversation_controller.router)
