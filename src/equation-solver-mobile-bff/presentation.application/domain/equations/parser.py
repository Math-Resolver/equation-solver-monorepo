from collections.abc import Callable


class ParsedEquation:
    def __init__(self, raw: str, equations: list[str]):
        self.raw = raw
        self.equations = equations


def parse_equation_input(raw: str) -> tuple[ParsedEquation | None, str | None]:
    """Parse equation input and return (parsed, error) without raising exceptions."""
    normalized = raw.strip()
    text_error = _run_validators(normalized, (_validate_not_empty,))
    if text_error is not None:
        return None, text_error

    equations = _split_and_normalize_equations(normalized)

    equations_error = _run_validators(
        equations,
        (_validate_equations_exist, _validate_equation_format),
    )
    if equations_error is not None:
        return None, equations_error

    return ParsedEquation(raw=normalized, equations=equations), None


def _validate_not_empty(text: str) -> str | None:
    if text:
        return None
    return "A equação não pode ser vazia"


def _split_and_normalize_equations(text: str) -> list[str]:
    text_with_commas = text.replace("\n", ",")
    raw_parts = text_with_commas.split(",")
    return [part.strip() for part in raw_parts if part.strip()]


def _validate_equations_exist(equations: list[str]) -> str | None:
    if equations:
        return None
    return "Nenhuma equação encontrada no payload"


def _validate_equation_format(equations: list[str]) -> str | None:
    for eq in equations:
        if _is_valid_mathematical_expression(eq):
            continue
        return f"Formato inválido: '{eq}'"
    return None


def _is_valid_mathematical_expression(expression: str) -> bool:
    normalized = expression.strip()
    
    has_numbers = any(char.isdigit() for char in normalized)
    has_operators_or_equals = any(op in normalized for op in "+-*/=^")
    
    has_function = any(func in normalized.lower() for func in ["fator(", "factorize(", "raiz(", "sqrt("])
    
    return has_numbers and (has_operators_or_equals or has_function)


def _run_validators[
    T
](
    value: T,
    validators: tuple[Callable[[T], str | None], ...],
) -> str | None:
    for validator in validators:
        error = validator(value)
        if error is not None:
            return error
    return None
