import re

from sympy import Eq, Interval, S, Symbol, Union, diff, nroots, oo, solveset
from sympy.calculus.util import continuous_domain
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from domain.equations.strategies.models.models_solver import SolveResult, StepResult
from domain.equations.strategies.strategy_solver import EquationSolverStrategy


X = Symbol("x", real=True)

LOCAL_DICT = {
    "x": X,
    "sin": __import__("sympy").sin,
    "cos": __import__("sympy").cos,
    "tan": __import__("sympy").tan,
    "log": __import__("sympy").log,
    "ln": __import__("sympy").log,
    "sqrt": __import__("sympy").sqrt,
    "exp": __import__("sympy").exp,
    "E": __import__("sympy").E,
    "pi": __import__("sympy").pi,
}


class FunctionAnalysisSolverStrategy(EquationSolverStrategy):
    def solve(self, expression: str, show_steps: bool) -> SolveResult:
        return solve_function_analysis(expression, show_steps)


def solve_function_analysis(expression: str, show_steps: bool) -> SolveResult:
    normalized = expression.strip()
    analysis_type, payload = _parse_request(normalized)

    solvers = {
        "domain": _solve_domain,
        "extrema": _solve_extrema,
        "intersection": _solve_intersection,
    }
    solver = solvers.get(analysis_type)
    if solver is None:
        return SolveResult(result="", steps=[], error="Informe domain:, extrema: ou intersect: para analisar funções")

    result_text, steps, error = solver(payload, show_steps)

    if error is not None:
        return SolveResult(result="", steps=[], error=error)

    return SolveResult(result=result_text or "", steps=steps if show_steps else [])


def _parse_request(expression: str) -> tuple[str, str]:
    lowered = expression.lower()

    prefixed = _detect_prefixed_request(expression, lowered)
    if prefixed is not None:
        return prefixed

    inferred = _detect_inferred_request(expression, lowered)
    if inferred is not None:
        return inferred

    return "", expression


def _detect_prefixed_request(expression: str, lowered: str) -> tuple[str, str] | None:
    prefix_rules = (
        ("domain", ("domain:", "dominio:", "domínio:")),
        ("extrema", ("extrema:", "maximum:", "minimum:")),
        ("intersection", ("intersect:", "interseccao:", "intersecao:", "interseção:")),
    )

    for analysis_type, prefixes in prefix_rules:
        if any(lowered.startswith(prefix) for prefix in prefixes):
            return analysis_type, expression.split(":", 1)[1].strip()

    return None


def _detect_inferred_request(expression: str, lowered: str) -> tuple[str, str] | None:
    inferred_rules = (
        ("domain", ("dominio", "domínio")),
        ("extrema", ("extremos", "extrema")),
        ("intersection", ("intersec",)),
    )

    payload = expression.split(":", 1)[1].strip() if ":" in expression else expression

    for analysis_type, keywords in inferred_rules:
        if any(keyword in lowered for keyword in keywords):
            return analysis_type, payload

    return None


def _parse_function(expr: str):
    normalized = expr.replace("^", "**")
    transformations = standard_transformations + (convert_xor, implicit_multiplication_application)
    parsed = parse_expr(normalized, transformations=transformations, local_dict=LOCAL_DICT)

    if X not in parsed.free_symbols:
        return None, "A função precisa depender de x"

    return parsed, None


def _solve_domain(expr: str, show_steps: bool) -> tuple[str | None, list[StepResult], str | None]:
    parsed, parse_error = _parse_function(expr)
    if parse_error is not None:
        return None, [], parse_error
    domain = continuous_domain(parsed, X, S.Reals)
    result = f"Domínio: { _format_set(domain) }"
    steps = [StepResult(rule="Analisa restrições de denominador, raiz e log", before=expr, after=result)]
    return result, steps if show_steps else [], None


def _solve_extrema(expr: str, show_steps: bool) -> tuple[str | None, list[StepResult], str | None]:
    parsed, parse_error = _parse_function(expr)
    if parse_error is not None:
        return None, [], parse_error
    derivative = diff(parsed, X)
    critical_points = solveset(Eq(derivative, 0), X, domain=S.Reals)

    if not critical_points.is_FiniteSet:
        return None, [], "Não foi possível determinar extremos automaticamente para essa função"

    analyses = []
    second_derivative = diff(parsed, X, 2)
    for point in critical_points:
        value = parsed.subs(X, point)
        curvature = second_derivative.subs(X, point)
        kind = _classify_curvature(curvature)
        analyses.append(f"{kind} em x = {_format_number(point)} com y = {_format_number(value)}")

    result = "Extremos: " + "; ".join(analyses)
    steps = [
        StepResult(rule="Deriva a função", before=expr, after=f"f'(x) = {derivative}"),
        StepResult(rule="Resolve f'(x) = 0", before=f"f'(x) = {derivative}", after=result),
    ]
    return result, steps if show_steps else [], None


def _solve_intersection(expr: str, show_steps: bool) -> tuple[str | None, list[StepResult], str | None]:
    before = expr
    expr = expr.strip()

    expr, other_expr = _split_intersection_operands(expr)

    parsed, parse_error = _parse_function(expr)
    if parse_error is not None:
        return None, [], parse_error

    if other_expr:
        return _solve_intersection_with_other(parsed, other_expr, expr, before, show_steps)

    return _solve_intersection_with_axis(parsed, expr, show_steps)


def _solve_intersection_with_other(parsed, other_expr: str, expr: str, before: str, show_steps: bool) -> tuple[str | None, list[StepResult], str | None]:
    """Solve intersection of two functions."""
    other_parsed, other_error = _parse_function(other_expr)
    if other_error is not None:
        return None, [], other_error
    
    solutions = solveset(Eq(parsed, other_parsed), X, domain=S.Reals)
    if not solutions.is_FiniteSet:
        return None, [], "Não foi possível calcular a interseção automaticamente"
    
    points = [f"({_format_number(point)}, {_format_number(parsed.subs(X, point))})" for point in solutions]
    result = "Interseções: " + ", ".join(points)
    steps = [
        StepResult(rule="Iguala as funções", before=before, after=f"{parsed} = {other_parsed}"),
        StepResult(rule="Resolve a equação resultante", before=f"{parsed} = {other_parsed}", after=result)
    ]
    return result, steps if show_steps else [], None


def _solve_intersection_with_axis(parsed, expr: str, show_steps: bool) -> tuple[str | None, list[StepResult], str | None]:
    """Solve intersection with x and y axes."""
    roots = solveset(Eq(parsed, 0), X, domain=S.Reals)
    
    result_parts = []
    if roots.is_FiniteSet:
        root_text = ", ".join(f"x = {_format_number(root)}" for root in roots)
        result_parts.append(f"Interseções com o eixo x: {root_text}")
    else:
        result_parts.append("Interseções com o eixo x: não determinadas automaticamente")
    
    y_intercept = parsed.subs(X, 0)
    if y_intercept.is_real:
        result_parts.append(f"eixo y em (0, {_format_number(y_intercept)})")
    
    result = "; ".join(result_parts)
    steps = [StepResult(rule="Resolve f(x) = 0", before=expr, after=result)]
    return result, steps if show_steps else [], None


def _format_set(domain) -> str:
    if isinstance(domain, Interval):
        return _format_interval(domain)
    if isinstance(domain, Union):
        return " ∪ ".join(_format_set(part) for part in domain.args)
    return str(domain).replace("oo", "∞")


def _format_interval(interval: Interval) -> str:
    left = "(" if interval.left_open else "["
    right = ")" if interval.right_open else "]"
    start = "-∞" if interval.start is -oo else _format_number(interval.start)
    end = "∞" if interval.end is oo else _format_number(interval.end)
    return f"{left}{start}, {end}{right}"


def _format_number(value) -> str:
    if value is oo:
        return "∞"
    if value is -oo:
        return "-∞"
    if hasattr(value, "is_Integer") and value.is_Integer:
        return str(int(value))
    if hasattr(value, "is_Rational") and value.is_Rational:
        return str(value)
    value_text = str(value)
    if not re.fullmatch(r"[+-]?\d+(?:\.\d+)?", value_text):
        return value_text
    numeric = float(value_text)
    if numeric.is_integer():
        return str(int(numeric))
    return (f"{numeric:.10f}").rstrip("0").rstrip(".")


def _classify_curvature(curvature) -> str:
    if curvature.is_real and curvature > 0:
        return "mínimo local"
    if curvature.is_real and curvature < 0:
        return "máximo local"
    return "ponto crítico"


def _split_intersection_operands(expr: str) -> tuple[str, str | None]:
    for separator in ("with", "and"):
        split_result = re.split(rf"\s+{separator}\s+", expr, maxsplit=1, flags=re.IGNORECASE)
        if len(split_result) == 2:
            left, right = split_result
            return left.strip(), right.strip()
    return expr, None