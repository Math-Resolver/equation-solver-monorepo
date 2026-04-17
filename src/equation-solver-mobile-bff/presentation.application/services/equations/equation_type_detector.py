from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from services.equations.parser import ParsedEquation


class EquationType(str, Enum):
    LINEAR = "linear"
    QUADRATIC = "quadratic"
    SYSTEM = "system"
    EXPRESSION = "expression"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class DetectionRule:
    equation_type: EquationType
    predicate: Callable[[str], bool]


def _is_quadratic(equation: str) -> bool:
    return "x^2" in equation or "x**2" in equation


def _is_linear(equation: str) -> bool:
    return "x" in equation


def detect_equation_type(parsed: ParsedEquation) -> EquationType:
    if len(parsed.equations) > 1:
        return EquationType.SYSTEM

    equation = parsed.equations[0].replace(" ", "")

    for rule in DETECTION_RULES:
        if rule.predicate(equation):
            return rule.equation_type

    return EquationType.UNKNOWN


def _is_simple_expression(equation: str) -> bool:
    has_numbers = any(char.isdigit() for char in equation)
    has_operators = any(op in equation for op in "+-*/")
    
    return has_numbers and has_operators


DETECTION_RULES: tuple[DetectionRule, ...] = (
    DetectionRule(equation_type=EquationType.QUADRATIC, predicate=_is_quadratic),
    DetectionRule(equation_type=EquationType.LINEAR, predicate=_is_linear),
    DetectionRule(equation_type=EquationType.EXPRESSION, predicate=_is_simple_expression),
)
