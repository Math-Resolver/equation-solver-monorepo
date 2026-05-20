from collections.abc import Callable
from enum import Enum
import re

from domain.equations.parser import ParsedEquation


class EquationType(str, Enum):
    LINEAR = "linear"
    QUADRATIC = "quadratic"
    SYSTEM = "system"
    EXPRESSION = "expression"
    FACTORIZATION = "factorization"
    FRACTION = "fraction"
    INEQUALITY = "inequality"
    SIMPLIFICATION = "simplification"
    FUNCTION_ANALYSIS = "function_analysis"
    STATISTICS = "statistics"
    UNKNOWN = "unknown"

def _is_quadratic(equation: str) -> bool:
    return _detect_polynomial_degree(equation) == 2


def _is_linear(equation: str) -> bool:
    return _detect_polynomial_degree(equation) == 1


def _is_factorization(equation: str) -> bool:
    """Check if the equation is a factorization request."""
    return any(func in equation.lower() for func in ["fator(", "factorize("])


def _is_fraction(equation: str) -> bool:
    """Check if the equation is an integer-fraction operation.

    Keep decimal divisions (e.g. 1.5/0.5) in the expression solver.
    """
    normalized = equation.replace(" ", "")

    if "x" in normalized.lower():
        return False

    if "." in normalized:
        return False

    has_fraction_token = bool(re.search(r"\d+/\d+", normalized))
    has_only_fraction_chars = bool(re.fullmatch(r"[0-9+\-*/()]+", normalized))

    return has_fraction_token and has_only_fraction_chars


def _is_inequality(equation: str) -> bool:
    """Check if the equation is an inequality."""
    return any(op in equation for op in ["<", ">", "<=", ">="])


def _is_simplification(equation: str) -> bool:
    """Check if the equation is a simplification request."""
    lowered = equation.lower()
    has_variable = bool(re.search(r"(?<![a-zA-Z])[xyz](?![a-zA-Z])", lowered))
    has_operators = any(op in equation for op in "+-*")
    no_equation_markers = "=" not in equation and not any(op in equation for op in ["<", ">"])
    no_functions = not any(func in lowered for func in ["raiz(", "sqrt(", "fator(", "factorize("])
    
    return has_variable and has_operators and no_equation_markers and no_functions


def _is_function_analysis(equation: str) -> bool:
    """Check if the equation requests function analysis."""
    lowered = equation.lower()
    return any(
        keyword in lowered
        for keyword in [
            "domain:",
            "dominio:",
            "domínio:",
            "extrema:",
            "maximum:",
            "minimum:",
            "intersect:",
            "interseccao:",
            "interseção:",
            "intersecao:",
            "interseção",
            "dominio",
            "domínio",
            "extremos",
        ]
    )


def _is_statistics(equation: str) -> bool:
    lowered = equation.lower()
    return any(
        lowered.startswith(prefix)
        for prefix in (
            "media:",
            "média:",
            "mediana:",
            "moda:",
            "combina:",
            "combinação:",
            "combinacao:",
            "ncr:",
        )
    )


def _is_simple_expression(equation: str) -> bool:
    has_numbers = any(char.isdigit() for char in equation)
    has_operators = any(op in equation for op in "+-*/" "^")
    has_functions = any(func in equation.lower() for func in ["sqrt(", "raiz("])
    
    return has_numbers and (has_operators or has_functions)


def _detect_polynomial_degree(equation: str) -> int | None:
    normalized = equation.replace(" ", "").replace("**", "^").lower()

    if "x" not in normalized:
        return None

    if "x^2" in normalized:
        return 2

    linear_pattern = r"(^|[+\-*/=(])x($|[+\-*/=)])|(^|[+\-*/=(])\d+\*?x($|[+\-*/=)])"
    if re.search(linear_pattern, normalized):
        return 1

    return None


def detect_equation_type(parsed: ParsedEquation) -> EquationType:
    if len(parsed.equations) > 1:
        return EquationType.SYSTEM

    equation = parsed.equations[0].replace(" ", "")

    for rule in DETECTION_RULES:
        equation_type, predicate = rule
        if predicate(equation):
            return equation_type

    return EquationType.UNKNOWN


DETECTION_RULES: tuple[tuple[EquationType, Callable[[str], bool]], ...] = (
    (EquationType.FACTORIZATION, _is_factorization),
    (EquationType.FUNCTION_ANALYSIS, _is_function_analysis),
    (EquationType.INEQUALITY, _is_inequality),
    (EquationType.FRACTION, _is_fraction),
    (EquationType.QUADRATIC, _is_quadratic),
    (EquationType.SIMPLIFICATION, _is_simplification),
    (EquationType.LINEAR, _is_linear),
    (EquationType.STATISTICS, _is_statistics),
    (EquationType.EXPRESSION, _is_simple_expression),
)
