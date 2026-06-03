import re

from sympy import Eq, Interval, S, Symbol, Union, diff, oo, solveset, zoo
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


SolveOutcome = tuple[str | None, list[StepResult], str | None, object | None]


def solve_function_analysis(expression: str, show_steps: bool) -> SolveResult:
    analysis_type, payload = _parse_request(expression.strip())

    solvers = {
        "domain": _solve_domain,
        "extrema": _solve_extrema,
        "intersection": _solve_intersection,
    }
    
    solver = solvers.get(analysis_type)
    if not solver:
        return SolveResult(result="", steps=[], error="Informe domain:, extrema: ou intersect: para analisar funções")

    result_text, steps, error, graph_expr = solver(payload, show_steps)
    if error:
        return SolveResult(result="", steps=[], error=error)

    graph = _build_function_graph(graph_expr) if graph_expr is not None else None
    return SolveResult(result=result_text or "", steps=steps if show_steps else [], graph=graph)


def _parse_request(expression: str) -> tuple[str, str]:
    lowered = expression.lower()
    return (_detect_prefixed_request(expression, lowered) or 
            _detect_inferred_request(expression, lowered) or 
            ("", expression))


def _detect_prefixed_request(expression: str, lowered: str) -> tuple[str, str] | None:
    prefix_rules = (
        ("domain", ("domain:",)),
        ("extrema", ("extrema:", "maximum:", "minimum:")),
        ("intersection", ("intersect:",)),
    )
    return next(((kind, expression.split(":", 1)[1].strip()) 
                 for kind, prefixes in prefix_rules 
                 if any(lowered.startswith(p) for p in prefixes)), None)


def _detect_inferred_request(expression: str, lowered: str) -> tuple[str, str] | None:
    inferred_rules = (
        ("domain", ("domain", "dominio", "domínio")),
        ("extrema", ("extremos", "extrema")),
        ("intersection", ("intersec",)),
    )
    payload = expression.split(":", 1)[1].strip() if ":" in expression else expression
    return next(((kind, payload) 
                 for kind, keywords in inferred_rules 
                 if any(kw in lowered for kw in keywords)), None)


def _parse_function(expr: str):
    normalized = expr.replace("^", "**")
    validation_error = _validate_function_expression(normalized)
    
    if validation_error:
        return None, validation_error

    transformations = standard_transformations + (convert_xor, implicit_multiplication_application)
    parsed = parse_expr(normalized, transformations=transformations, local_dict=LOCAL_DICT)

    return (parsed, None) if X in parsed.free_symbols else (None, "A função precisa depender de x")


def _validate_function_expression(expr: str) -> str | None:
    rules = [
        (not expr.strip(), "Expressão vazia"),
        (not re.fullmatch(r"[0-9A-Za-z_+\-*/^().,\s]+", expr), "Expressão contém caracteres inválidos"),
        (expr.count("(") != expr.count(")"), "Parênteses desbalanceados")
    ]
    return next((msg for condition, msg in rules if condition), None)


def _solve_domain(expr: str, show_steps: bool) -> SolveOutcome:
    parsed, parse_error = _parse_function(expr)
    if parse_error:
        return None, [], parse_error, None

    result = f"Domínio: {_format_set(continuous_domain(parsed, X, S.Reals))}"
    steps = [StepResult(rule="Analisa restrições de denominador, raiz e log", before=expr, after=result)]
    
    return result, steps if show_steps else [], None, parsed


def _solve_extrema(expr: str, show_steps: bool) -> SolveOutcome:
    parsed, parse_error = _parse_function(expr)
    if parse_error:
        return None, [], parse_error, None

    derivative = diff(parsed, X)
    critical_points = solveset(Eq(derivative, 0), X, domain=S.Reals)

    if not critical_points.is_FiniteSet:
        return None, [], "Não foi possível determinar extremos automaticamente para essa função", None

    second_derivative = diff(parsed, X, 2)
    analyses = [
        f"{_classify_curvature(second_derivative.subs(X, p))} em x = {_format_number(p)} com y = {_format_number(parsed.subs(X, p))}"
        for p in critical_points
    ]

    result = f"Extremos: {'; '.join(analyses)}"
    steps = [
        StepResult(rule="Deriva a função", before=expr, after=f"f'(x) = {derivative}"),
        StepResult(rule="Resolve f'(x) = 0", before=f"f'(x) = {derivative}", after=result),
    ]
    return result, steps if show_steps else [], None, parsed


def _solve_intersection(expr: str, show_steps: bool) -> SolveOutcome:
    before = expr
    expr, other_expr = _split_intersection_operands(expr.strip())

    parsed, parse_error = _parse_function(expr)
    if parse_error:
        return None, [], parse_error, None

    return (_solve_intersection_with_other(parsed, other_expr, expr, before, show_steps) 
            if other_expr else 
            _solve_intersection_with_axis(parsed, expr, show_steps))


def _solve_intersection_with_other(parsed, other_expr: str, expr: str, before: str, show_steps: bool) -> SolveOutcome:
    other_parsed, other_error = _parse_function(other_expr)
    if other_error:
        return None, [], other_error, None
    
    solutions = solveset(Eq(parsed, other_parsed), X, domain=S.Reals)
    if not solutions.is_FiniteSet:
        return None, [], "Não foi possível calcular a interseção automaticamente", None
    
    points = [f"({_format_number(p)}, {_format_number(parsed.subs(X, p))})" for p in solutions]
    result = f"Interseções: {', '.join(points)}"
    
    steps = [
        StepResult(rule="Iguala as funções", before=before, after=f"{parsed} = {other_parsed}"),
        StepResult(rule="Resolve a equação resultante", before=f"{parsed} = {other_parsed}", after=result)
    ]
    return result, steps if show_steps else [], None, parsed


def _solve_intersection_with_axis(parsed, expr: str, show_steps: bool) -> SolveOutcome:
    roots = solveset(Eq(parsed, 0), X, domain=S.Reals)
    
    root_text = ", ".join(f"x = {_format_number(r)}" for r in roots) if roots.is_FiniteSet else "não determinadas automaticamente"
    result_parts = [f"Interseções com o eixo x: {root_text}"]
    
    y_intercept = parsed.subs(X, 0)
    if getattr(y_intercept, "is_real", False):
        result_parts.append(f"eixo y em (0, {_format_number(y_intercept)})")
    
    result = "; ".join(result_parts)
    steps = [StepResult(rule="Resolve f(x) = 0", before=expr, after=result)]
    
    return result, steps if show_steps else [], None, parsed


def _build_function_graph(parsed_expr, num_points: int = 41) -> dict:
    candidates = _collect_graph_candidates(parsed_expr)
    center, span = _resolve_graph_window(candidates)
    span = max(2.0, min(span, 200.0))

    step = span / (num_points - 1)
    return {
        "kind": "function", 
        "samplePoints": [_sample_graph_point(parsed_expr, center - span / 2 + i * step) for i in range(num_points)]
    }


def _collect_graph_candidates(parsed_expr) -> list[float]:
    candidates = []
    candidates.extend(_extract_numeric_points(solveset(Eq(parsed_expr, 0), X, domain=S.Reals)))
    candidates.extend(_extract_numeric_points(solveset(Eq(diff(parsed_expr, X), 0), X, domain=S.Reals)))

    if _to_float(parsed_expr.subs(X, 0)) is not None:
        candidates.append(0.0)

    return candidates


def _extract_numeric_points(points_set) -> list[float]:
    return [val for p in points_set if (val := _to_float(p)) is not None] if points_set.is_FiniteSet else []


def _to_float(value) -> float | None:
    if value is None or _is_non_plotable_value(value):
        return None

    numeric_text = str(value.evalf() if hasattr(value, "evalf") else value)
    return float(numeric_text) if re.fullmatch(r"[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", numeric_text) else None


def _resolve_graph_window(candidates: list[float]) -> tuple[float, float]:
    if not candidates:
        return 0.0, 10.0

    left, right = min(candidates), max(candidates)
    return (left + right) / 2.0, max(2.0, (right - left) * 2.0)


def _sample_graph_point(parsed_expr, x: float) -> dict[str, float | None]:
    y_value = parsed_expr.subs(X, x).evalf()
    x_value = float(round(x, 6))

    y_numeric = _to_float(y_value)
    return {"x": x_value, "y": float(round(y_numeric, 6)) if y_numeric is not None else None}


def _is_non_plotable_value(value) -> bool:
    return (
        value in (oo, -oo, zoo, S.NaN) or
        getattr(value, "is_real", None) is False or
        getattr(value, "is_finite", None) is False
    )


def _format_set(domain) -> str:
    if isinstance(domain, Interval):
        return _format_interval(domain)
    if isinstance(domain, Union):
        return " ∪ ".join(_format_set(part) for part in domain.args)
    return str(domain).replace("oo", "∞")


def _format_interval(interval: Interval) -> str:
    left, right = ("(", ")") if interval.left_open and interval.right_open else \
                  ("(", "]") if interval.left_open else \
                  ("[", ")") if interval.right_open else ("[", "]")
    
    start = "-∞" if interval.start is -oo else _format_number(interval.start)
    end = "∞" if interval.end is oo else _format_number(interval.end)
    return f"{left}{start}, {end}{right}"


def _format_number(value) -> str:
    if value in (oo, -oo):
        return "∞" if value is oo else "-∞"
    if getattr(value, "is_Integer", False):
        return str(int(value))
    if getattr(value, "is_Rational", False):
        return str(value)

    val_str = str(value)
    if not re.fullmatch(r"[+-]?\d+(?:\.\d+)?", val_str):
        return val_str

    numeric = float(val_str)
    return str(int(numeric)) if numeric.is_integer() else f"{numeric:.10f}".rstrip("0").rstrip(".")


def _classify_curvature(curvature) -> str:
    is_real = getattr(curvature, "is_real", False)
    return "mínimo local" if is_real and curvature > 0 else (
           "máximo local" if is_real and curvature < 0 else "ponto crítico")


def _split_intersection_operands(expr: str) -> tuple[str, str | None]:
    parts = re.split(r"\s+(?:with|and)\s+", expr, maxsplit=1, flags=re.IGNORECASE)
    return (parts[0].strip(), parts[1].strip()) if len(parts) == 2 else (expr, None)