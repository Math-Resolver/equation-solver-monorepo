from pydantic import BaseModel, ConfigDict

from api.v1.conversation.schemas.solve_equation_response import Step


class EquationHistoryItemResponse(BaseModel):
    equation: str
    result: str
    steps: list[Step]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "equation": "2*x + 5 = 15",
                "result": "x = 5",
                "steps": [
                    {
                        "rule": "subtract 5 from both sides",
                        "before": "2*x + 5 = 15",
                        "after": "2*x = 10"
                    },
                    {
                        "rule": "divide both sides by 2",
                        "before": "2*x = 10",
                        "after": "x = 5"
                    }
                ]
            }
        }
    )
