import re

from services.equations.errors import InvalidEquationError
from services.solvers.models import SolveResult, StepResult
from services.solvers.strategy import EquationSolverStrategy


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
    if not operator:
        raise InvalidEquationError("Inequação deve conter um dos operadores: <, >, <=, >=")
    
    parts = normalized.split(operator)
    if len(parts) != 2:
        raise InvalidEquationError(f"Formato inválido de inequação")
    
    left_coeff, left_const = _parse_linear_expression(parts[0])
    right_coeff, right_const = _parse_linear_expression(parts[1])
    
    a = left_coeff - right_coeff
    b = right_const - left_const
    
    if abs(a) < 1e-12:
        raise InvalidEquationError("Inequação deve ter coeficiente de x diferente de zero")
    
    x_value = b / a
    
    if a < 0:
        operator = _flip_operator(operator)
    
    result_text = _format_inequality_result(x_value, operator)
    
    if not show_steps:
        return SolveResult(result=result_text, steps=[])
    
    steps = [
        StepResult(
            rule="Coloca variáveis de um lado e constantes do outro",
            before=inequality,
            after=f"{_format_number(a)}x {operator} {_format_number(b)}",
        ),
        StepResult(
            rule=f"Divide ambos os lados por {_format_number(a)}" + (" (inverte o operador pois dividimos por negativo)" if a < 0 else ""),
            before=f"{_format_number(a)}x {operator} {_format_number(b)}",
            after=result_text,
        ),
    ]
    
    return SolveResult(result=result_text, steps=steps)


def _extract_inequality_operator(expression: str) -> str | None:
    """Extract the inequality operator from the expression."""
    if "<=" in expression:
        return "<="
    if ">=" in expression:
        return ">="
    if "<" in expression:
        return "<"
    if ">" in expression:
        return ">"
    return None


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
    
    if prefix in ("", "+"):
        return 1.0
    if prefix == "-":
        return -1.0
    
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
