import cmath

from domain.equations.errors import InvalidEquationError
from domain.strategies.models import SolveResult, StepResult
from domain.strategies.strategy_solver import EquationSolverStrategy


class QuadraticSolverStrategy(EquationSolverStrategy):
    """Strategy for solving quadratic equations."""

    def solve(self, equation: str, show_steps: bool) -> SolveResult:
        return solve_quadratic(equation, show_steps)


def solve_quadratic(equation: str, show_steps: bool) -> SolveResult:
    normalized = equation.replace(" ", "")
    a, b, c = _parse_quadratic_equation(normalized)

    if abs(a) < 1e-12:
        raise InvalidEquationError("Equação do segundo grau deve ter coeficiente a diferente de zero")

    delta = (b * b) - (4 * a * c)
    sqrt_delta = cmath.sqrt(delta)
    denominator = 2 * a

    x1 = (-b + sqrt_delta) / denominator
    x2 = (-b - sqrt_delta) / denominator
    result_text = f"x1 = {_format_number(x1)}, x2 = {_format_number(x2)}"

    if not show_steps:
        return SolveResult(result=result_text, steps=[])

    steps = [
        StepResult(
            rule="Identifica os coeficientes da equação",
            before=equation,
            after=f"a = {_format_number(a)}, b = {_format_number(b)}, c = {_format_number(c)}",
        ),
        StepResult(
            rule="Calcula o discriminante",
            before=f"Δ = b² - 4ac = {_format_number(b)}² - 4·{_format_number(a)}·{_format_number(c)}",
            after=f"Δ = {_format_number(delta)}",
        ),
        StepResult(
            rule="Aplica a fórmula de Bhaskara",
            before="x = (-b ± √Δ) / 2a",
            after=result_text,
        ),
    ]

    return SolveResult(result=result_text, steps=steps)


def _parse_quadratic_equation(equation: str) -> tuple[float, float, float]:
    if "=" not in equation:
        raise InvalidEquationError("Equação do segundo grau deve conter '='")

    left, right = equation.split("=", 1)
    left_a, left_b, left_c = _parse_quadratic_side(left)
    right_a, right_b, right_c = _parse_quadratic_side(right)

    return left_a - right_a, left_b - right_b, left_c - right_c


def _parse_quadratic_side(expression: str) -> tuple[float, float, float]:
    normalized = expression.replace("**", "^")

    if not normalized:
        return 0.0, 0.0, 0.0

    normalized = normalized.replace("-", "+-")
    if normalized.startswith("+-"):
        normalized = normalized[1:]

    a = 0.0
    b = 0.0
    c = 0.0

    for term in (part for part in normalized.split("+") if part):
        if "x^2" in term:
            a += _extract_coefficient(term, "x^2")
        elif "x" in term:
            b += _extract_coefficient(term, "x")
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


def _format_number(value: complex | float) -> str:
    if isinstance(value, complex):
        if abs(value.imag) < 1e-12:
            return _format_number(value.real)

        real_part = _format_number(value.real)
        imaginary_part = _format_number(abs(value.imag))
        sign = "+" if value.imag >= 0 else "-"
        return f"{real_part} {sign} {imaginary_part}i"

    if isinstance(value, float):
        rounded = round(value, 10)
        if rounded.is_integer():
            return str(int(rounded))
        return (f"{rounded:.10f}").rstrip("0").rstrip(".")

    return str(value)
