from dataclasses import dataclass


@dataclass(frozen=True)
class ExplanationModel:
    message: str
    example: str | None = None