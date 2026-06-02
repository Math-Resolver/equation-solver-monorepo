import cmath

from domain.equations.strategies.models.models_solver import SolveResult, StepResult
from domain.equations.strategies.strategy_solver import EquationSolverStrategy


class QuadraticSolverStrategy(EquationSolverStrategy):
    """Strategy for solving quadratic equations."""

    def solve(self, equation: str, show_steps: bool) -> SolveResult:
        return solve_quadratic(equation, show_steps)


def solve_quadratic(equation: str, show_steps: bool) -> SolveResult:
    normalized = equation.replace(" ", "")
    parsed, parse_error = _parse_quadratic_equation(normalized)
    if parse_error is not None:
        return SolveResult(result="", steps=[], error=parse_error)

    a, b, c = parsed
    if abs(a) < 1e-12:
        return SolveResult(result="", steps=[], error="Equação do segundo grau deve ter coeficiente a diferente de zero")

    delta = (b * b) - (4 * a * c)
    sqrt_delta = cmath.sqrt(delta)
    denominator = 2 * a

    x1 = (-b + sqrt_delta) / denominator
    x2 = (-b - sqrt_delta) / denominator
    result_text = f"x1 = {_format_number(x1)}, x2 = {_format_number(x2)}"
    graph = _build_quadratic_graph(a=a, b=b, c=c, x1=x1, x2=x2)

    if not show_steps:
        return SolveResult(result=result_text, steps=[], graph=graph)

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
    return SolveResult(result=result_text, steps=steps, graph=graph)


def _build_quadratic_graph(a: float, b: float, c: float, x1: complex, x2: complex) -> dict:
    vertex_x = -b / (2 * a)
    vertex_y = (a * vertex_x * vertex_x) + (b * vertex_x) + c

    return {
        "kind": "quadratic",
        "expression": f"f(x) = {_format_number(a)}x^2 + {_format_number(b)}x + {_format_number(c)}",
        "coefficients": {
            "a": float(a),
            "b": float(b),
            "c": float(c),
        },
        "roots": [_format_number(x1), _format_number(x2)],
        "vertex": {
            "x": float(vertex_x),
            "y": float(vertex_y),
        },
    }


def _parse_quadratic_equation(equation: str) -> tuple[tuple[float, float, float] | None, str | None]:
    if "=" not in equation:
        return None, "Equação do segundo grau deve conter '='"

    left, right = equation.split("=", 1)
    left_side, left_error = _parse_quadratic_side(left)
    if left_error is not None:
        return None, left_error
    right_side, right_error = _parse_quadratic_side(right)
    if right_error is not None:
        return None, right_error

    left_a, left_b, left_c = left_side
    right_a, right_b, right_c = right_side

    return (left_a - right_a, left_b - right_b, left_c - right_c), None


def _parse_quadratic_side(expression: str) -> tuple[tuple[float, float, float] | None, str | None]:
    normalized = expression.replace("**", "^")

    if not normalized:
        return 0.0, 0.0, 0.0

    normalized = normalized.replace("-", "+-")
    if normalized.startswith("+-"):
        normalized = normalized[1:]

    coefficients = {"quadratic": 0.0, "linear": 0.0, "constant": 0.0}

    for term in (part for part in normalized.split("+") if part):
        term_type = _classify_quadratic_term(term)
        
        if term_type == "constant":
            if not _is_number(term):
                return None, f"Formato inválido na expressão: '{expression}'"
            coefficients["constant"] += float(term)
        else:
            symbol = "x^2" if term_type == "quadratic" else "x"
            coefficients[term_type] += _extract_coefficient(term, symbol)

    return (coefficients["quadratic"], coefficients["linear"], coefficients["constant"]), None


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


def _is_number(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if stripped[0] in "+-":
        stripped = stripped[1:]
    return stripped.replace(".", "", 1).isdigit()


def _classify_quadratic_term(term: str) -> str:
    if "x^2" in term:
        return "quadratic"
    if "x" in term:
        return "linear"
    return "constant"
