from dataclasses import dataclass


@dataclass
class StepResult:
    rule: str
    before: str
    after: str


@dataclass
class SolveResult:
    result: str
    steps: list[StepResult]
