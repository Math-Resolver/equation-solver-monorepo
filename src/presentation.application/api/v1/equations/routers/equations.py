from fastapi import APIRouter, BackgroundTasks, Request, status
from fastapi.responses import JSONResponse

from api.v1.conversation.schemas.solve_equation_request import SolveEquationRequest
from api.v1.conversation.schemas.solve_equation_response import SolveEquationResponse, Step
from domain.equations.dispatcher import dispatch_solver, is_supported_equation_type
from domain.equations.equation_type_detector import EquationType
import api.v1.routers.equations as compat_routers_equations
from domain.equations.parser import parse_equation_input
from api.v1.dependencies.service_injection import EquationHistory, EquationHistoryRepository
router = APIRouter(prefix="/v1/equation", tags=["equation"])


def _extract_username_from_request(request: Request) -> str | None:
    auth_header = request.headers.get("Authorization", "")

    if not _is_valid_bearer_token(auth_header):
        return None

    token = auth_header.replace("Bearer ", "", 1).strip()
    return _extract_username_from_dev_token(token)


def _is_valid_bearer_token(auth_header: str) -> bool:
    return bool(auth_header) and auth_header.startswith("Bearer ")


def _extract_username_from_dev_token(token: str) -> str | None:
    if not token.startswith("dev-user:"):
        return None
    return token.split(":", 1)[1] or None


@router.post("/solve", response_model=SolveEquationResponse)
async def solve_equation(
    payload: SolveEquationRequest,
    request: Request,
    background_tasks: BackgroundTasks,
) -> SolveEquationResponse:
    parsed, parse_error = parse_equation_input(payload.equation)
    if parse_error is not None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": parse_error},
        )

    equation_type = compat_routers_equations.detect_equation_type(parsed)
    if equation_type == EquationType.UNKNOWN or not is_supported_equation_type(equation_type):
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": "Tipo de equação não suportada para resolução"},
        )

    result = dispatch_solver(parsed=parsed, equation_type=equation_type, show_steps=payload.showSteps)

    if result.error is not None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": result.error},
        )

    if await request.is_disconnected():
        return JSONResponse(
            status_code=499,
            content={"detail": "Client disconnected"},
        )
    response_steps = [
        Step(rule=step.rule, before=step.before, after=step.after)
        for step in result.steps
    ]

    username = _extract_username_from_request(request)
    if username:
        entity = EquationHistory(
            username=username,
            equation=payload.equation,
            result=result.result,
            steps=[step.model_dump() for step in response_steps],
        )
        background_tasks.add_task(
            EquationHistoryRepository(collection=None).save,
            entity,
        )

    return SolveEquationResponse(result=result.result, steps=response_steps)
