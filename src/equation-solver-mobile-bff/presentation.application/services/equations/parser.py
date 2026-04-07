from services.equations.errors import InvalidEquationError


class ParsedEquation:
    def __init__(self, raw: str, equations: list[str]):
        self.raw = raw
        self.equations = equations


def parse_equation_input(raw: str) -> ParsedEquation:
    normalized = raw.strip()
    if not normalized:
        raise InvalidEquationError("A equação não pode ser vazia")

    equations = [part.strip() for part in normalized.replace("\n", ",").split(",") if part.strip()]
    if not equations:
        raise InvalidEquationError("Nenhuma equação encontrada no payload")

    for eq in equations:
        if "=" not in eq:
            raise InvalidEquationError(f"Formato de equação inválido: '{eq}'")

    return ParsedEquation(raw=normalized, equations=equations)
