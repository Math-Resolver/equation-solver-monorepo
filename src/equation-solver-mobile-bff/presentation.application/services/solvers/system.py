from services.equations.errors import InvalidEquationError
from services.solvers.models import SolveResult, StepResult
from services.solvers.strategy import EquationSolverStrategy


class SystemSolverStrategy(EquationSolverStrategy):
    """Strategy for solving system of equations."""

    def solve(self, equations: list[str], show_steps: bool) -> SolveResult:
        return solve_system(equations, show_steps)


def solve_system(equations: list[str], show_steps: bool) -> SolveResult:
    if len(equations) != 2:
        raise InvalidEquationError("O sistema deve conter exatamente duas equações")

    a1, b1, c1 = _parse_linear_equation(equations[0])
    a2, b2, c2 = _parse_linear_equation(equations[1])

    determinant = (a1 * b2) - (a2 * b1)
    if abs(determinant) < 1e-12:
        raise InvalidEquationError("O sistema não possui solução única")

    x_value = ((c1 * b2) - (c2 * b1)) / determinant
    y_value = ((a1 * c2) - (a2 * c1)) / determinant
    result_text = f"x = {_format_number(x_value)}, y = {_format_number(y_value)}"

    if not show_steps:
        return SolveResult(result=result_text, steps=[])

    steps = [
        StepResult(
            rule="Coloca o sistema na forma ax + by = c",
            before="\n".join(equations),
            after=(
                f"{_format_number(a1)}x + {_format_number(b1)}y = {_format_number(c1)}\n"
                f"{_format_number(a2)}x + {_format_number(b2)}y = {_format_number(c2)}"
            ),
        ),
        StepResult(
            rule="Calcula o determinante",
            before=f"Δ = {_format_number(a1)}·{_format_number(b2)} - {_format_number(a2)}·{_format_number(b1)}",
            after=f"Δ = {_format_number(determinant)}",
        ),
        StepResult(
            rule="Aplica a regra de Cramer",
            before="x = (c1b2 - c2b1) / Δ, y = (a1c2 - a2c1) / Δ",
            after=result_text,
        ),
    ]

    return SolveResult(result=result_text, steps=steps)


def _parse_linear_equation(equation: str) -> tuple[float, float, float]:
    normalized = equation.replace(" ", "")
    if "=" not in normalized:
        raise InvalidEquationError("Cada equação do sistema deve conter '='")

    left, right = normalized.split("=", 1)
    left_x, left_y, left_c = _parse_linear_side(left)
    right_x, right_y, right_c = _parse_linear_side(right)

    return left_x - right_x, left_y - right_y, right_c - left_c


def _parse_linear_side(expression: str) -> tuple[float, float, float]:
    normalized = expression.replace("-", "+-")
    if normalized.startswith("+-"):
        normalized = normalized[1:]

    a = 0.0
    b = 0.0
    c = 0.0

    for term in (part for part in normalized.split("+") if part):
        if "x" in term:
            a += _extract_coefficient(term, "x")
        elif "y" in term:
            b += _extract_coefficient(term, "y")
        else:
            c += float(term)

    return a, b, c


def _extract_coefficient(term: str, symbol: str) -> float:
    prefix = term.split(symbol, 1)[0].replace("*", "")

    if prefix in ("", "+"):
        return 1.0
    if prefix == "-":
        return -1.0

    return float(prefix)


def _format_number(value: float) -> str:
    rounded = round(value, 10)
    if rounded.is_integer():
        return str(int(rounded))
    return (f"{rounded:.10f}").rstrip("0").rstrip(".")
