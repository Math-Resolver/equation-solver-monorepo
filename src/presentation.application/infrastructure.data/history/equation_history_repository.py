import logging
from domain.equations.history.entities import EquationHistory

logger = logging.getLogger(__name__)

class EquationHistoryRepository:
    def __init__(self, collection):
        self._collection = collection

    async def save(self, entity: EquationHistory) -> None:
        await self._collection.update_one(
            filter={"username": entity.username, "equation": entity.equation, "createdAt": entity.created_at},
            update={"$set": {"result": entity.result, "steps": entity.steps}},
            upsert=True,
        )   
        
def get_history_repository(collection=None):
    if collection is None:
        return None
    return EquationHistoryRepository(collection=collection)
        