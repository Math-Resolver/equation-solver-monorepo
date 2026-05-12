from collections.abc import Callable

from domain.equations.strategies.models.models_solver import SolveResult, StepResult
from domain.equations.strategies.strategy_solver import EquationSolverStrategy


NumberExtractor = Callable[[str], str | None]


class FactorizationSolverStrategy(EquationSolverStrategy):
    """Strategy for factorizing numbers."""

    def solve(self, equation: str, show_steps: bool) -> SolveResult:
        return solve_factorization(equation, show_steps)


def solve_factorization(input_str: str, show_steps: bool) -> SolveResult:
    """
    Factorize a number into its prime factors.
    
    Args:
        input_str: A number to factorize (e.g., "12", "fator(60)")
        show_steps: Whether to include factorization steps
    
    Returns:
        SolveResult with the prime factorization
    """
    normalized = input_str.strip()
    number_str = _extract_number_text(normalized)
    
    if not _is_integer_text(number_str):
        return SolveResult(result="", steps=[], error=f"Número inválido para fatoração: '{number_str}'")

    number = int(number_str)

    if number < 2:
        return SolveResult(result="", steps=[], error="O número deve ser maior ou igual a 2 para fatoração")

    factors = _get_prime_factors(number)
    result_text = _format_factorization(factors)

    if not show_steps:
        return SolveResult(result=result_text, steps=[])

    steps = _generate_factorization_steps(number, factors)
    return SolveResult(result=result_text, steps=steps)


def _get_prime_factors(n: int) -> list[int]:
    """Get prime factors of a number."""
    factors = []
    d = 2
    
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    
    if n > 1:
        factors.append(n)
    
    return factors


def _format_factorization(factors: list[int]) -> str:
    """Format prime factors as a string."""
    if not factors:
        return "1"
    
    factor_groups = {}
    for factor in factors:
        factor_groups[factor] = factor_groups.get(factor, 0) + 1
    
    parts = []
    for factor in sorted(factor_groups.keys()):
        count = factor_groups[factor]
        if count == 1:
            parts.append(str(factor))
        else:
            parts.append(f"{factor}^{count}")
    
    return " × ".join(parts)


def _generate_factorization_steps(number: int, factors: list[int]) -> list[StepResult]:
    """Generate step-by-step factorization."""
    steps = []
    current = number
    
    for factor in factors:
        next_val = current // factor
        steps.append(
            StepResult(
                rule=f"Divide por {factor}",
                before=str(current),
                after=str(next_val),
            )
        )
        current = next_val
    
    result_text = _format_factorization(factors)
    steps.append(
        StepResult(
            rule="Fatoração completa",
            before=str(number),
            after=result_text,
        )
    )
    
    return steps


def _extract_number_text(input_text: str) -> str:
    for extractor in _NUMBER_EXTRACTORS:
        extracted = extractor(input_text)
        if extracted is not None:
            return extracted

    return input_text


def _extract_from_wrapped_call(input_text: str) -> str | None:
    lowered = input_text.lower()
    if not lowered.startswith("fator(") and not lowered.startswith("factorize("):
        return None

    return input_text[input_text.index("(") + 1:input_text.rindex(")")].strip()


def _extract_plain_number(input_text: str) -> str | None:
    return input_text


_NUMBER_EXTRACTORS: tuple[NumberExtractor, ...] = (
    _extract_from_wrapped_call,
    _extract_plain_number,
)


def _is_integer_text(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if stripped[0] in "+-":
        return stripped[1:].isdigit()
    return stripped.isdigit()
