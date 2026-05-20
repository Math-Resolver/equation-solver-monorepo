import logging
from unittest.mock import MagicMock

logger = logging.getLogger(__name__)

#substituir por MongoDB 
# from motor.asyncio import AsyncIOMotorClient
# client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
# collection = client["equation_history"]["EquationHistory"]

collection = MagicMock()

async def save_equation_history(
    username: str,
    equation: str,
    result: str,
    steps: list[dict],
    created_at: str,
) -> None:
    await collection.update_one(
        {"username": username, "equation": equation,"createdAt": created_at},
        {"$set": {"result": result, "steps": steps}},
        upsert=True,
    )


async def schedule_history_persistence(
    username: str,
    equation: str,
    result: str,
    steps: list[dict],
     created_at: str,
) -> None:
    await save_equation_history(
        username=username,
        equation=equation,
        result=result,
        steps=steps,
        created_at=created_at,
    )
