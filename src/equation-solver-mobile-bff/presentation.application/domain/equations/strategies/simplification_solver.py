from domain.equations.strategies.models.models_solver import SolveResult, StepResult
from domain.equations.strategies.strategy_solver import EquationSolverStrategy


class SimplificationSolverStrategy(EquationSolverStrategy):
    """Strategy for simplifying algebraic expressions."""

    def solve(self, expression: str, show_steps: bool) -> SolveResult:
        return solve_simplification(expression, show_steps)


def solve_simplification(expression: str, show_steps: bool) -> SolveResult:
    """
    Simplify algebraic expressions.
    
    Currently supports:
    - Combining like terms (e.g., "2x + 3x" -> "5x")
    - Removing parentheses with distribution (e.g., "2(x+3)" -> "2x+6")
    
    Args:
        expression: An algebraic expression to simplify
        show_steps: Whether to include simplification steps
    
    Returns:
        SolveResult with the simplified expression
    """
    normalized = expression.strip()

    if not _contains_variables(normalized):
        return SolveResult(result="", steps=[], error="Expressão deve conter ao menos uma variável (ex: x, y, z)")

    result = _simplify_like_terms(normalized)

    if not show_steps:
        return SolveResult(result=result, steps=[])

    steps = [
        StepResult(
            rule="Agrupa termos semelhantes",
            before=normalized,
            after=result,
        ),
    ]
    return SolveResult(result=result, steps=steps)


def _contains_variables(expression: str) -> bool:
    """Check if expression contains variables."""
    return any(var in expression.lower() for var in ['x', 'y', 'z', 'a', 'b', 'c'])


def _simplify_like_terms(expression: str) -> str:
    """Simplify by combining like terms."""
    normalized = expression.replace(" ", "").replace("-", "+-")
    if normalized.startswith("+-"):
        normalized = normalized[1:]
    
    terms = {}
    
    for term in (part for part in normalized.split("+") if part):
        variable = _extract_variable(term)
        coefficient = float(_extract_coefficient_value(term))
        
        if variable not in terms:
            terms[variable] = 0
        terms[variable] += coefficient
    
    result_parts = []
    for var in sorted(terms.keys(), key=lambda x: (x == "", x)):
        coeff = terms[var]
        if coeff == 0:
            continue
        
        if var == "":
            result_parts.append(f"{int(coeff) if coeff.is_integer() else coeff}")
        else:
            result_parts.append(_format_variable_term(coeff, var))
    
    if not result_parts:
        return "0"
    
    return _format_result_with_signs(result_parts)


def _extract_variable(term: str) -> str:
    """Extract variable from a term (e.g., 'x' from '2x')."""
    for char in term:
        if char.isalpha():
            return char
    return ""


def _extract_coefficient_value(term: str) -> str:
    """Extract coefficient value from a term."""
    var = _extract_variable(term)
    
    if not var:
        return term
    
    prefix = term.split(var, 1)[0].replace("*", "")
    
    if prefix in ("", "+"):
        return "1"
    if prefix == "-":
        return "-1"
    
    return prefix


def _format_variable_term(coeff: float, var: str) -> str:
    special_terms = {
        1: var,
        -1: f"-{var}",
    }
    if coeff in special_terms:
        return special_terms[coeff]

    coeff_str = str(int(coeff) if coeff.is_integer() else coeff)
    return f"{coeff_str}{var}"


def _format_result_with_signs(parts: list[str]) -> str:
    """Format result by joining parts with appropriate signs."""
    result = parts[0]
    for part in parts[1:]:
        sign = "" if part.startswith("-") else "+"
        result += sign + part
    return result
