from pydantic import BaseModel, Field


class SolveEquationRequest(BaseModel):
    equation: str = Field(min_length=3, description="Expressão da equação")
    showSteps: bool = Field(default=True)


class Step(BaseModel):
    rule: str
    before: str
    after: str


class SolveEquationResponse(BaseModel):
    result: str
    steps: list[Step]
