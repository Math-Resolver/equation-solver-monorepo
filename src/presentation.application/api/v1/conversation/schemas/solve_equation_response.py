from pydantic import BaseModel


class Step(BaseModel):
    rule: str
    before: str
    after: str


class GraphPoint(BaseModel):
    x: float
    y: float | None = None


class SolveEquationGraph(BaseModel):
    kind: str
    expression: str | None = None
    coefficients: dict[str, float] | None = None
    roots: list[str] | None = None
    vertex: GraphPoint | None = None
    samplePoints: list[GraphPoint] | None = None


class SolveEquationResponse(BaseModel):
    result: str
    steps: list[Step]
    graph: SolveEquationGraph | None = None
