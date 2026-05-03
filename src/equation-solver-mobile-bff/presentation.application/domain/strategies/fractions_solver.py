import re
from fractions import Fraction

from domain.equations.errors import InvalidEquationError
from domain.strategies.models_solver import SolveResult, StepResult
from domain.strategies.strategy_solver import EquationSolverStrategy


class FractionSolverStrategy(EquationSolverStrategy):
    """Strategy for solving fraction operations."""

    def solve(self, equation: str, show_steps: bool) -> SolveResult:
        return solve_fraction(equation, show_steps)


def solve_fraction(expression: str, show_steps: bool) -> SolveResult:
    """
    Solve fraction operations.
    
    Args:
        expression: A fraction operation (e.g., "1/2 + 1/3")
        show_steps: Whether to include solution steps
    
    Returns:
        SolveResult with the fraction result
    """
    normalized = expression.strip()
    _validate_fraction_expression(normalized)
    
    result_value = _evaluate_fraction_expression(normalized)
    result_text = _format_fraction(result_value)

    if not show_steps:
        return SolveResult(result=result_text, steps=[])

    steps = _generate_fraction_steps(normalized, result_text)
    return SolveResult(result=result_text, steps=steps)


def _validate_fraction_expression(expression: str) -> None:
    """Validate that the expression contains only fraction-safe characters."""
    allowed_chars = set("0123456789+-*/(). ")
    if not all(c in allowed_chars for c in expression):
        raise InvalidEquationError(f"Expressão de fração contém caracteres inválidos: '{expression}'")
    
    if "//" in expression:
        raise InvalidEquationError(f"Formato inválido para fração: '{expression}'")


def _evaluate_fraction_expression(expression: str) -> Fraction:
    """
    Evaluate a fraction expression using Python's Fraction class.
    
    Args:
        expression: A fraction operation string
    
    Returns:
        Fraction result
    """
    normalized = expression.replace(" ", "")
    
    try:
        def replace_fraction(match):
            return f"Fraction({match.group(1)},{match.group(2)})"
        
        converted = re.sub(r'(\d+)\s*/\s*(\d+)', replace_fraction, normalized)
        
        result = eval(converted, {"__builtins__": {}, "Fraction": Fraction})
        return result
    except (ValueError, ZeroDivisionError, SyntaxError) as e:
        raise InvalidEquationError(f"Erro ao avaliar fração: {str(e)}")





def _format_fraction(frac: Fraction) -> str:
    """Format a Fraction object as a string."""
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"{frac.numerator}/{frac.denominator}"


def _generate_fraction_steps(expression: str, final_result: str) -> list[StepResult]:
    """Generate step-by-step fraction resolution."""
    steps = []
    
    steps.append(
        StepResult(
            rule="Calcula a fração",
            before=expression,
            after=final_result,
        )
    )
    
    return steps
