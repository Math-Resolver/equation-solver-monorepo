import re

from domain.equations.strategies.models.models_solver import SolveResult, StepResult
from domain.equations.strategies.strategy_solver import EquationSolverStrategy


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

    operator = _extract_inequality_operator(normalized)
    if operator is None:
        return SolveResult(result="", steps=[], error="Inequação deve conter um dos operadores: <, >, <=, >=")

    split_result, split_error = _split_inequality(normalized, operator)
    if split_error is not None:
        return SolveResult(result="", steps=[], error=split_error)
    left_expression, right_expression = split_result

    left_parse, left_parse_error = _parse_linear_expression(left_expression)
    if left_parse_error is not None:
        return SolveResult(result="", steps=[], error=left_parse_error)
    right_parse, right_parse_error = _parse_linear_expression(right_expression)
    if right_parse_error is not None:
        return SolveResult(result="", steps=[], error=right_parse_error)

    left_coeff, left_const = left_parse
    right_coeff, right_const = right_parse

    a = left_coeff - right_coeff
    b = right_const - left_const

    if abs(a) < 1e-12:
        return SolveResult(result="", steps=[], error="Inequação deve ter coeficiente de x diferente de zero")

    solution_operator = _flip_operator(operator) if a < 0 else operator
    result_text = _format_inequality_result(b / a, solution_operator)

    if not show_steps:
        return SolveResult(result=result_text, steps=[])

    reduction = f"{_format_number(a)}x {solution_operator} {_format_number(b)}"
    steps = _build_solution_steps(inequality, a, b, reduction, result_text)

    return SolveResult(result=result_text, steps=steps)


def _extract_inequality_operator(expression: str) -> str | None:
    """Extract the inequality operator from the expression."""
    return next((operator for operator in _INEQUALITY_OPERATORS if operator in expression), None)


def _split_inequality(expression: str, operator: str) -> tuple[tuple[str, str] | None, str | None]:
    parts = expression.split(operator)
    if len(parts) != 2:
        return None, "Formato inválido de inequação"
    return (parts[0], parts[1]), None


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


def _parse_linear_expression(expression: str) -> tuple[tuple[float, float] | None, str | None]:
    """Parse a linear expression to extract coefficient of x and constant."""
    normalized = expression.replace("**", "^").replace("-", "+-")
    if normalized.startswith("+-"):
        normalized = normalized[1:]
    
    coeff = 0.0
    const = 0.0
    
    for term in (part for part in normalized.split("+") if part):
        if "x" in term:
            parsed_coeff, coeff_error = _extract_coefficient(term, "x")
            if coeff_error is not None:
                return None, coeff_error
            coeff += parsed_coeff
        else:
            if not _is_number(term):
                return None, "Formato inválido de inequação"
            const += float(term)
    
    return (coeff, const), None


def _extract_coefficient(term: str, symbol: str) -> tuple[float | None, str | None]:
    """Extract the coefficient from a term."""
    prefix = term.split(symbol, 1)[0].replace("*", "")

    special_coefficients = {
        "": 1.0,
        "+": 1.0,
        "-": -1.0,
    }

    if prefix in special_coefficients:
        return special_coefficients[prefix], None

    if not _is_number(prefix):
        return None, "Formato inválido de inequação"
    return float(prefix), None


def _is_number(text: str) -> bool:
    return bool(re.fullmatch(r"[+-]?\d+(?:\.\d+)?", text))


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
