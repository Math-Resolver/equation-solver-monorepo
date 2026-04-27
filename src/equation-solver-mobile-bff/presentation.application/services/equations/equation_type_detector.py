from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
import re

from services.equations.parser import ParsedEquation


class EquationType(str, Enum):
    LINEAR = "linear"
    QUADRATIC = "quadratic"
    SYSTEM = "system"
    EXPRESSION = "expression"
    FACTORIZATION = "factorization"
    FRACTION = "fraction"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class DetectionRule:
    equation_type: EquationType
    predicate: Callable[[str], bool]


def _is_quadratic(equation: str) -> bool:
    return "x^2" in equation or "x**2" in equation


def _is_linear(equation: str) -> bool:
    return "x" in equation


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


def _is_simple_expression(equation: str) -> bool:
    has_numbers = any(char.isdigit() for char in equation)
    has_operators = any(op in equation for op in "+-*/" "^")
    has_functions = any(func in equation.lower() for func in ["sqrt(", "raiz("])
    
    return has_numbers and (has_operators or has_functions)


def detect_equation_type(parsed: ParsedEquation) -> EquationType:
    if len(parsed.equations) > 1:
        return EquationType.SYSTEM

    equation = parsed.equations[0].replace(" ", "")

    for rule in DETECTION_RULES:
        if rule.predicate(equation):
            return rule.equation_type

    return EquationType.UNKNOWN


DETECTION_RULES: tuple[DetectionRule, ...] = (
    DetectionRule(equation_type=EquationType.FACTORIZATION, predicate=_is_factorization),
    DetectionRule(equation_type=EquationType.QUADRATIC, predicate=_is_quadratic),
    DetectionRule(equation_type=EquationType.LINEAR, predicate=_is_linear),
    DetectionRule(equation_type=EquationType.FRACTION, predicate=_is_fraction),
    DetectionRule(equation_type=EquationType.EXPRESSION, predicate=_is_simple_expression),
)
