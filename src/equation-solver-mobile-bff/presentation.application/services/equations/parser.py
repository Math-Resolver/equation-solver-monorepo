from services.equations.errors import InvalidEquationError


class ParsedEquation:
    def __init__(self, raw: str, equations: list[str]):
        self.raw = raw
        self.equations = equations


def parse_equation_input(raw: str) -> ParsedEquation:
    normalized = raw.strip()
    _validate_not_empty(normalized)

    equations = _split_and_normalize_equations(normalized)
    _validate_equations_exist(equations)
    _validate_equation_format(equations)

    return ParsedEquation(raw=normalized, equations=equations)


def _validate_not_empty(text: str) -> None:
    if not text:
        raise InvalidEquationError("A equação não pode ser vazia")


def _split_and_normalize_equations(text: str) -> list[str]:
    text_with_commas = text.replace("\n", ",")
    raw_parts = text_with_commas.split(",")
    return [part.strip() for part in raw_parts if part.strip()]


def _validate_equations_exist(equations: list[str]) -> None:
    if not equations:
        raise InvalidEquationError("Nenhuma equação encontrada no payload")


def _validate_equation_format(equations: list[str]) -> None:
    for eq in equations:
        if _is_valid_mathematical_expression(eq):
            continue
        raise InvalidEquationError(f"Formato inválido: '{eq}'")


def _is_valid_mathematical_expression(expression: str) -> bool:
    normalized = expression.strip()
    
    has_numbers = any(char.isdigit() for char in normalized)
    has_operators_or_equals = any(op in normalized for op in "+-*/=")
    
    return has_numbers and has_operators_or_equals
