import re

from services.equations.errors import InvalidEquationError
from services.solvers.models import SolveResult, StepResult


def solve_linear(equation: str, show_steps: bool) -> SolveResult:
    compact = equation.replace(" ", "")

    match = re.fullmatch(r"([+-]?\d*)\*?x([+-]\d+)?=([+-]?\d+)", compact)
    if not match:
        raise InvalidEquationError("Equação linear deve ser do seguinte formato: '2*x+5=15'")

    a_raw, b_raw, c_raw = match.groups()

    if a_raw in ("", "+"):
        a = 1
    elif a_raw == "-":
        a = -1
    else:
        a = int(a_raw)

    b = int(b_raw) if b_raw else 0
    c = int(c_raw)

    if a == 0:
        raise InvalidEquationError("O coeficiente de x não pode ser zero")

    rhs_after_subtract = c - b
    x_value = rhs_after_subtract / a

    result_text = f"x = {int(x_value) if x_value.is_integer() else x_value}"

    if not show_steps:
        return SolveResult(result=result_text, steps=[])

    steps = [
        StepResult(
            rule=f"Subtrai {b} de ambos os lados",
            before=f"{a}x + {b} = {c}",
            after=f"{a}x = {rhs_after_subtract}",
        ),
        StepResult(
            rule=f"Divide ambos os lados por {a}",
            before=f"{a}x = {rhs_after_subtract}",
            after=result_text,
        ),
    ]

    return SolveResult(result=result_text, steps=steps)
