from pydantic import BaseModel


class Step(BaseModel):
    rule: str
    before: str
    after: str


class SolveEquationResponse(BaseModel):
    result: str
    steps: list[Step]
