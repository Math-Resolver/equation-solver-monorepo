import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Protocol

logger = logging.getLogger(__name__)

@dataclass
class EquationHistory:
    username: str
    equation: str
    result: str
    steps: list[dict]
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    id: Optional[str] = None

class IEquationHistoryRepository(Protocol):
    async def save(self, entity: EquationHistory) -> None: ...

class EquationHistoryRepository:
    def __init__(self, collection):
        self._collection = collection

    async def save(self, entity: EquationHistory) -> None:
        await self._collection.update_one(
            filter={"username": entity.username, "equation": entity.equation, "createdAt": entity.created_at},
            update={"$set": {"result": entity.result, "steps": entity.steps}},
            upsert=True,
        )