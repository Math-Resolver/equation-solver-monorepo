from typing import Protocol
from domain.equations.history.entities import EquationHistory

class IEquationHistoryRepository(Protocol):
    async def save(self, entity: EquationHistory) -> None: ...