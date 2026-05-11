from domain.equations.strategies.models.models_solver import SolveResult, StepResult
from domain.equations.strategies.strategy_solver import EquationSolverStrategy


class SystemSolverStrategy(EquationSolverStrategy):
    """Strategy for solving system of equations."""

    def solve(self, equations: list[str], show_steps: bool) -> SolveResult:
        return solve_system(equations, show_steps)


def solve_system(equations: list[str], show_steps: bool) -> SolveResult:
    if len(equations) != 2:
        return SolveResult(result="", steps=[], error="O sistema deve conter exatamente duas equações")

    parsed_1, parse_error_1 = _parse_linear_equation(equations[0])
    if parse_error_1 is not None:
        return SolveResult(result="", steps=[], error=parse_error_1)

    parsed_2, parse_error_2 = _parse_linear_equation(equations[1])
    if parse_error_2 is not None:
        return SolveResult(result="", steps=[], error=parse_error_2)

    a1, b1, c1 = parsed_1
    a2, b2, c2 = parsed_2

    determinant = (a1 * b2) - (a2 * b1)
    if abs(determinant) < 1e-12:
        return SolveResult(result="", steps=[], error="O sistema não possui solução única")

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


def _parse_linear_equation(equation: str) -> tuple[tuple[float, float, float] | None, str | None]:
    normalized = equation.replace(" ", "")
    if "=" not in normalized:
        return None, "Cada equação do sistema deve conter '='"

    left, right = normalized.split("=", 1)
    left_side, left_error = _parse_linear_side(left)
    if left_error is not None:
        return None, left_error
    right_side, right_error = _parse_linear_side(right)
    if right_error is not None:
        return None, right_error

    left_x, left_y, left_c = left_side
    right_x, right_y, right_c = right_side

    return (left_x - right_x, left_y - right_y, right_c - left_c), None


def _parse_linear_side(expression: str) -> tuple[tuple[float, float, float] | None, str | None]:
    normalized = expression.replace("-", "+-")
    if normalized.startswith("+-"):
        normalized = normalized[1:]

    coefficients = {"x": 0.0, "y": 0.0, "constant": 0.0}

    for term in (part for part in normalized.split("+") if part):
        term_type = _classify_system_term(term)
        
        if term_type == "constant":
            if not _is_number(term):
                return None, f"Formato inválido em termo do sistema: '{term}'"
            coefficients["constant"] += float(term)
        else:
            coefficients[term_type] += _extract_coefficient(term, term_type)

    return (coefficients["x"], coefficients["y"], coefficients["constant"]), None


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


def _is_number(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if stripped[0] in "+-":
        stripped = stripped[1:]
    return stripped.replace(".", "", 1).isdigit()


def _classify_system_term(term: str) -> str:
    if "x" in term:
        return "x"
    if "y" in term:
        return "y"
    return "constant"
