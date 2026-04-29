from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from api.v1.schemas.equation import SolveEquationRequest, SolveEquationResponse, Step
from services.equations.dispatcher import dispatch_solver
from services.equations.equation_type_detector import EquationType, detect_equation_type
from services.equations.errors import InvalidEquationError, UnsupportedEquationTypeError
from services.equations.parser import parse_equation_input
from services.history.persistence import schedule_history_persistence

router = APIRouter(prefix="/v1/equation", tags=["equation"])


def _extract_username_from_request(request: Request) -> str | None:
    # TODO: implementar autenticação de verdade e extrair o username do token JWT
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.replace("Bearer ", "", 1).strip()
    if token.startswith("dev-user:"):
        return token.split(":", 1)[1] or None

    return None


@router.post("/solve", response_model=SolveEquationResponse)
async def solve_equation(
    payload: SolveEquationRequest,
    request: Request,
    background_tasks: BackgroundTasks,
) -> SolveEquationResponse:
    try:
        parsed = parse_equation_input(payload.equation)
        equation_type = detect_equation_type(parsed)

        if equation_type == EquationType.UNKNOWN:
            raise UnsupportedEquationTypeError("Tipo de equação não suportada para resolução")

        result = dispatch_solver(parsed=parsed, equation_type=equation_type, show_steps=payload.showSteps)
    except InvalidEquationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except UnsupportedEquationTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    if await request.is_disconnected():
        raise HTTPException(status_code=499, detail="Client disconnected")

    response_steps = [
        Step(rule=step.rule, before=step.before, after=step.after)
        for step in result.steps
    ]

    username = _extract_username_from_request(request)
    if username:
        background_tasks.add_task(
            schedule_history_persistence,
            username=username,
            equation=payload.equation,
            result=result.result,
            steps=[step.model_dump() for step in response_steps],
        )

    return SolveEquationResponse(result=result.result, steps=response_steps)
