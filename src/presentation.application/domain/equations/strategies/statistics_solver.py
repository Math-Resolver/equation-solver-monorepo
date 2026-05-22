from collections import Counter
import math
import re
from abc import ABC, abstractmethod
from statistics import mean, median

from domain.equations.strategies.models.models_solver import SolveResult, StepResult
from domain.equations.strategies.strategy_solver import EquationSolverStrategy


class StatisticsSolverStrategy(EquationSolverStrategy):
    def solve(self, equation: str, show_steps: bool) -> SolveResult:
        return solve_statistics(equation, show_steps)


class _StatisticsOperationStrategy(ABC):
    @abstractmethod
    def solve(self, expression: str, values: list[float], show_steps: bool) -> SolveResult:
        raise NotImplementedError


class _MeanStatisticsStrategy(_StatisticsOperationStrategy):
    def solve(self, expression: str, values: list[float], show_steps: bool) -> SolveResult:
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


class _MedianStatisticsStrategy(_StatisticsOperationStrategy):
    def solve(self, expression: str, values: list[float], show_steps: bool) -> SolveResult:
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


class _ModeStatisticsStrategy(_StatisticsOperationStrategy):
    def solve(self, expression: str, values: list[float], show_steps: bool) -> SolveResult:
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


class _CombinationStatisticsStrategy(_StatisticsOperationStrategy):
    def solve(self, expression: str, values: list[float], show_steps: bool) -> SolveResult:
        validation_error = _validate_combination_values(values)
        if validation_error is not None:
            return SolveResult(result="", steps=[], error=validation_error)

        n, k = (int(values[0]), int(values[1]))
        result_text = str(math.comb(n, k))

        if not show_steps:
            return SolveResult(result=result_text, steps=[])

        numerator = math.factorial(n)
        denominator_left = math.factorial(k)
        denominator_right = math.factorial(n - k)
        denominator = denominator_left * denominator_right

        steps = [
            StepResult(
                rule="Aplica a fórmula de combinação",
                before=expression,
                after="C(n, k) = n! / (k! * (n-k)!)",
            ),
            StepResult(
                rule="Substitui os valores",
                before=expression,
                after=f"C({n}, {k}) = {n}! / ({k}! * ({n}-{k})!) = {numerator} / ({denominator_left} * {denominator_right})",
            ),
            StepResult(
                rule="Calcula o resultado final",
                before=expression,
                after=f"C({n}, {k}) = {numerator} / {denominator} = {result_text}",
            ),
        ]
        return SolveResult(result=result_text, steps=steps)


def solve_statistics(expression: str, show_steps: bool) -> SolveResult:
    normalized = expression.strip()
    operation, payload = _parse_statistics_request(normalized)

    if operation is None:
        return SolveResult(result="", steps=[], error="Operação estatística desconhecida. Use mean, median, mode ou combination.")

    values = _extract_numbers(payload)
    if not values and operation != "combination":
        return SolveResult(result="", steps=[], error="Informe uma lista de números válida")

    strategy = _STATISTICS_STRATEGIES[operation]
    return strategy.solve(normalized, values, show_steps)


def _parse_statistics_request(expression: str) -> tuple[str | None, str]:
    lowered = expression.lower()
    prefixes = (
        ("mean", ("mean:",)),
        ("median", ("median:",)),
        ("mode", ("mode:",)),
        ("combination", ("combination:",)),
    )

    for operation, candidates in prefixes:
        for prefix in candidates:
            if lowered.startswith(prefix):
                return operation, expression.split(":", 1)[1].strip()

    return None, ""


def _extract_numbers(payload: str) -> list[float]:
    matches = re.findall(r"[+-]?\d+(?:[\.,]\d+)?", payload)
    return [float(match.replace(",", ".")) for match in matches]


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
        return f"Mode: {formatted[0]}"
    return f"Modes: {', '.join(formatted)}"


def _format_frequency_map(counts: Counter[float]) -> str:
    formatted_items = [f"{_format_number(value)}: {count}" for value, count in sorted(counts.items())]
    return ", ".join(formatted_items)


def _validate_combination_values(values: list[float]) -> str | None:
    if len(values) != 2:
        return "Combinação exige exatamente dois números: n e k"

    n_value, k_value = values
    if not n_value.is_integer() or not k_value.is_integer():
        return "Combinação aceita apenas números inteiros"

    n = int(n_value)
    k = int(k_value)
    if n < 0 or k < 0 or k > n:
        return "Combinação exige 0 <= k <= n"

    return None


_STATISTICS_STRATEGIES: dict[str, _StatisticsOperationStrategy] = {
    "mean": _MeanStatisticsStrategy(),
    "median": _MedianStatisticsStrategy(),
    "mode": _ModeStatisticsStrategy(),
    "combination": _CombinationStatisticsStrategy(),
}