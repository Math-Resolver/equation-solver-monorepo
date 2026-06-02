from dataclasses import dataclass
from typing import Optional


@dataclass
class StepResult:
    rule: str
    before: str
    after: str


@dataclass
class SolveResult:
    result: str
    steps: list[StepResult]
    error: Optional[str] = None
    graph: Optional[dict] = None
