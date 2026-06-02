from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class EquationHistoryEntity:
    username: str
    equation: str
    result: str
    steps: list[dict]
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    id: Optional[str] = None