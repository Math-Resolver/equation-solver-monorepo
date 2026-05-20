from collections import Counter
import math
import re
from statistics import mean, median

from domain.equations.strategies.models.models_solver import SolveResult, StepResult
from domain.equations.strategies.strategy_solver import EquationSolverStrategy


class StatisticsSolverStrategy(EquationSolverStrategy):
    """Strategy for solving basic statistics requests."""

    def solve(self, equation: str, show_steps: bool) -> SolveResult:
        return solve_statistics(equation, show_steps)


def solve_statistics(expression: str, show_steps: bool) -> SolveResult:
    normalized = expression.strip()
    operation, payload = _parse_statistics_request(normalized)

    if operation is None:
        return SolveResult(result="", steps=[], error="Informe media:, mediana:, moda: ou combina:")

    values = _extract_numbers(payload)
    if operation == "combination":
        return _solve_combination(values, normalized, show_steps)

    if not values:
        return SolveResult(result="", steps=[], error="Informe uma lista de números válida")

    if operation == "mean":
        return _solve_mean(values, normalized, show_steps)
    if operation == "median":
        return _solve_median(values, normalized, show_steps)
    return _solve_mode(values, normalized, show_steps)


def _parse_statistics_request(expression: str) -> tuple[str | None, str]:
    lowered = expression.lower()
    prefixes = (
        ("mean", ("media:", "média:")),
        ("median", ("mediana:",)),
        ("mode", ("moda:",)),
        ("combination", ("combina:", "combinação:", "combinacao:", "ncr:")),
    )

    for operation, candidates in prefixes:
        for prefix in candidates:
            if lowered.startswith(prefix):
                return operation, expression.split(":", 1)[1].strip()

    return None, ""


def _extract_numbers(payload: str) -> list[float]:
    matches = re.findall(r"[+-]?\d+(?:[\.,]\d+)?", payload)
    return [float(match.replace(",", ".")) for match in matches]


def _solve_mean(values: list[float], expression: str, show_steps: bool) -> SolveResult:
    result_value = mean(values)
    result_text = _format_number(result_value)

    if not show_steps:
        return SolveResult(result=result_text, steps=[])

    steps = [
        StepResult(
            rule="Soma os valores e divide pela quantidade",
            before=expression,
            after=f"{_format_number(sum(values))} / {len(values)} = {result_text}",
        )
    ]
    return SolveResult(result=result_text, steps=steps)


def _solve_median(values: list[float], expression: str, show_steps: bool) -> SolveResult:
    ordered_values = sorted(values)
    result_value = median(ordered_values)
    result_text = _format_number(result_value)

    if not show_steps:
        return SolveResult(result=result_text, steps=[])

    steps = [
        StepResult(
            rule="Ordena os valores e escolhe o elemento central",
            before=expression,
            after=f"{_format_sequence(ordered_values)} -> {result_text}",
        )
    ]
    return SolveResult(result=result_text, steps=steps)


def _solve_mode(values: list[float], expression: str, show_steps: bool) -> SolveResult:
    counts = Counter(values)
    highest_frequency = max(counts.values())
    modes = [value for value, frequency in counts.items() if frequency == highest_frequency]
    result_text = _format_modes(modes)

    if not show_steps:
        return SolveResult(result=result_text, steps=[])

    steps = [
        StepResult(
            rule="Conta a frequência de cada valor",
            before=expression,
            after=f"{_format_frequency_map(counts)} -> {result_text}",
        )
    ]
    return SolveResult(result=result_text, steps=steps)


def _solve_combination(values: list[float], expression: str, show_steps: bool) -> SolveResult:
    if len(values) != 2:
        return SolveResult(result="", steps=[], error="Combinação exige exatamente dois números: n e k")

    n_value, k_value = values
    if not n_value.is_integer() or not k_value.is_integer():
        return SolveResult(result="", steps=[], error="Combinação aceita apenas números inteiros")

    n = int(n_value)
    k = int(k_value)
    if n < 0 or k < 0 or k > n:
        return SolveResult(result="", steps=[], error="Combinação exige 0 <= k <= n")

    result_text = str(math.comb(n, k))

    if not show_steps:
        return SolveResult(result=result_text, steps=[])

    steps = [
        StepResult(
            rule="Aplica a fórmula de combinação",
            before=expression,
            after=f"C({n}, {k}) = {result_text}",
        )
    ]
    return SolveResult(result=result_text, steps=steps)


def _format_number(value: float) -> str:
    rounded = round(value, 10)
    if rounded.is_integer():
        return str(int(rounded))
    return (f"{rounded:.10f}").rstrip("0").rstrip(".")


def _format_sequence(values: list[float]) -> str:
    return ", ".join(_format_number(value) for value in values)


def _format_modes(values: list[float]) -> str:
    formatted = [_format_number(value) for value in sorted(values)]
    if len(formatted) == 1:
        return f"Moda: {formatted[0]}"
    return f"Modas: {', '.join(formatted)}"


def _format_frequency_map(counts: Counter[float]) -> str:
    formatted_items = [f"{_format_number(value)}: {count}" for value, count in sorted(counts.items())]
    return ", ".join(formatted_items)