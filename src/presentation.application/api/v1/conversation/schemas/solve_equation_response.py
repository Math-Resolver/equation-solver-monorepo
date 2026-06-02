from pydantic import BaseModel


class Step(BaseModel):
    rule: str
    before: str
    after: str


class GraphPoint(BaseModel):
    x: float
    y: float


class SolveEquationGraph(BaseModel):
    kind: str
    expression: str
    coefficients: dict[str, float]
    roots: list[str]
    vertex: GraphPoint


class SolveEquationResponse(BaseModel):
    result: str
    steps: list[Step]
    graph: SolveEquationGraph | None = None
