from enum import Enum

from services.equations.parser import ParsedEquation


class EquationType(str, Enum):
    LINEAR = "linear"
    QUADRATIC = "quadratic"
    SYSTEM = "system"
    UNKNOWN = "unknown"


def detect_equation_type(parsed: ParsedEquation) -> EquationType:
    if len(parsed.equations) > 1:
        return EquationType.SYSTEM

    equation = parsed.equations[0].replace(" ", "")

    if "x^2" in equation or "x**2" in equation:
        return EquationType.QUADRATIC

    if "x" in equation:
        return EquationType.LINEAR

    return EquationType.UNKNOWN
