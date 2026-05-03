import re

from domain.equations.errors import InvalidEquationError
from domain.strategies.models import SolveResult, StepResult
from domain.strategies.strategy_solver import EquationSolverStrategy


class InequalitySolverStrategy(EquationSolverStrategy):
    """Strategy for solving inequalities."""

    def solve(self, inequality: str, show_steps: bool) -> SolveResult:
        return solve_inequality(inequality, show_steps)


def solve_inequality(inequality: str, show_steps: bool) -> SolveResult:
    """
    Solve first-degree inequalities.
    
    Args:
        inequality: An inequality like "2x + 5 > 13" or "3x - 2 <= 10"
        show_steps: Whether to include solution steps
    
    Returns:
        SolveResult with the solution interval
    """
    normalized = inequality.replace(" ", "")

    operator = _require_inequality_operator(normalized)
    left_expression, right_expression = _split_inequality(normalized, operator)
    left_coeff, left_const = _parse_linear_expression(left_expression)
    right_coeff, right_const = _parse_linear_expression(right_expression)

    a = left_coeff - right_coeff
    b = right_const - left_const

    _ensure_nonzero_coefficient(a)

    solution_operator = _flip_operator(operator) if a < 0 else operator
    result_text = _format_inequality_result(b / a, solution_operator)

    if not show_steps:
        return SolveResult(result=result_text, steps=[])

    reduction = f"{_format_number(a)}x {solution_operator} {_format_number(b)}"
    steps = _build_solution_steps(inequality, a, b, reduction, result_text)

    return SolveResult(result=result_text, steps=steps)


def _require_inequality_operator(expression: str) -> str:
    operator = _extract_inequality_operator(expression)
    if operator is None:
        raise InvalidEquationError("Inequação deve conter um dos operadores: <, >, <=, >=")
    return operator


def _extract_inequality_operator(expression: str) -> str | None:
    """Extract the inequality operator from the expression."""
    return next((operator for operator in _INEQUALITY_OPERATORS if operator in expression), None)


def _split_inequality(expression: str, operator: str) -> tuple[str, str]:
    parts = expression.split(operator)
    if len(parts) != 2:
        raise InvalidEquationError("Formato inválido de inequação")
    return parts[0], parts[1]


def _ensure_nonzero_coefficient(a: float) -> None:
    if abs(a) < 1e-12:
        raise InvalidEquationError("Inequação deve ter coeficiente de x diferente de zero")


def _build_solution_steps(
    inequality: str,
    a: float,
    b: float,
    reduction: str,
    result_text: str,
) -> list[StepResult]:
    inversion_note = " (inverte o operador pois dividimos por negativo)" if a < 0 else ""

    return [
        StepResult(
            rule="Coloca variáveis de um lado e constantes do outro",
            before=inequality,
            after=reduction,
        ),
        StepResult(
            rule=f"Divide ambos os lados por {_format_number(a)}{inversion_note}",
            before=reduction,
            after=result_text,
        ),
    ]


def _flip_operator(operator: str) -> str:
    """Flip inequality operator when multiplying/dividing by negative."""
    flips = {"<": ">", ">": "<", "<=": ">=", ">=": "<="}
    return flips[operator]


def _parse_linear_expression(expression: str) -> tuple[float, float]:
    """Parse a linear expression to extract coefficient of x and constant."""
    normalized = expression.replace("**", "^").replace("-", "+-")
    if normalized.startswith("+-"):
        normalized = normalized[1:]
    
    coeff = 0.0
    const = 0.0
    
    for term in (part for part in normalized.split("+") if part):
        if "x" in term:
            coeff += _extract_coefficient(term, "x")
        else:
            const += float(term)
    
    return coeff, const


def _extract_coefficient(term: str, symbol: str) -> float:
    """Extract the coefficient from a term."""
    prefix = term.split(symbol, 1)[0].replace("*", "")

    special_coefficients = {
        "": 1.0,
        "+": 1.0,
        "-": -1.0,
    }

    if prefix in special_coefficients:
        return special_coefficients[prefix]

    return float(prefix)


def _format_inequality_result(x_value: float, operator: str) -> str:
    """Format the inequality solution."""
    x_str = _format_number(x_value)
    return f"x {operator} {x_str}"


def _format_number(value: float) -> str:
    """Format a number for display."""
    rounded = round(value, 10)
    if rounded.is_integer():
        return str(int(rounded))
    return (f"{rounded:.10f}").rstrip("0").rstrip(".")


_INEQUALITY_OPERATORS = ("<=", ">=", "<", ">")
