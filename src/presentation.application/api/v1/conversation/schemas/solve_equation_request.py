from pydantic import BaseModel, Field


class SolveEquationRequest(BaseModel):
    equation: str = Field(min_length=3, description="Expressão da equação")
    showSteps: bool = Field(default=True)
