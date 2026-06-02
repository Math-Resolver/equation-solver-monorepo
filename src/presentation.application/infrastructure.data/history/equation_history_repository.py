import logging
from domain.equations.history.entities.equation_history_entity import EquationHistoryEntity

logger = logging.getLogger(__name__)

class EquationHistoryRepository:
    def __init__(self, collection):
        self._collection = collection

    async def save(self, entity: EquationHistoryEntity) -> None:
        try:
            await self._collection.update_one(
                filter={"username": entity.username, "equation": entity.equation, "createdAt": entity.created_at},
                update={"$set": {"result": entity.result, "steps": entity.steps}},
                upsert=True,
            )
        except Exception as e:
            logger.error(f"Failed to save equation history: {e}")
    
def get_history_repository(collection=None):
    if collection is None:
        return None
    return EquationHistoryRepository(collection=collection)
        