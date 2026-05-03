from dataclasses import dataclass


@dataclass(frozen=True)
class ExplanationModel:
    is_operation_successful: bool 
    message: str
    example: str | None = None