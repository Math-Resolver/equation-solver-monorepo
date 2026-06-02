from typing import Protocol
from domain.equations.history.entities.equation_history_entity import EquationHistoryEntity

class EquationHistoryRepositoryAbstraction(Protocol):
    async def save(self, entity: EquationHistoryEntity) -> None: ...