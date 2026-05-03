import re

from sympy import Eq, Interval, S, Symbol, Union, diff, nroots, oo, solveset
from sympy.calculus.util import continuous_domain
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from domain.equations.errors import InvalidEquationError
from domain.strategies.models.models_solver import SolveResult, StepResult
from domain.strategies.strategy_solver import EquationSolverStrategy


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

    if analysis_type == "domain":
        result_text, steps = _solve_domain(payload, show_steps)
    elif analysis_type == "extrema":
        result_text, steps = _solve_extrema(payload, show_steps)
    elif analysis_type == "intersection":
        result_text, steps = _solve_intersection(payload, show_steps)
    else:
        raise InvalidEquationError("Informe domain:, extrema: ou intersect: para analisar funções")

    return SolveResult(result=result_text, steps=steps if show_steps else [])


def _parse_request(expression: str) -> tuple[str, str]:
    lowered = expression.lower()

    for prefix in ("domain:", "dominio:", "domínio:"):
        if lowered.startswith(prefix):
            return "domain", expression.split(":", 1)[1].strip()

    for prefix in ("extrema:", "maximum:", "minimum:"):
        if lowered.startswith(prefix):
            return "extrema", expression.split(":", 1)[1].strip()

    for prefix in ("intersect:", "interseccao:", "intersecao:", "interseção:"):
        if lowered.startswith(prefix):
            return "intersection", expression.split(":", 1)[1].strip()

    if any(keyword in lowered for keyword in ("dominio", "domínio")):
        return "domain", expression.split(":", 1)[1].strip() if ":" in expression else expression
    if any(keyword in lowered for keyword in ("extremos", "extrema")):
        return "extrema", expression.split(":", 1)[1].strip() if ":" in expression else expression
    if "intersec" in lowered:
        return "intersection", expression.split(":", 1)[1].strip() if ":" in expression else expression

    return "", expression


def _parse_function(expr: str):
    normalized = expr.replace("^", "**")
    transformations = standard_transformations + (convert_xor, implicit_multiplication_application)
    try:
        parsed = parse_expr(normalized, transformations=transformations, local_dict=LOCAL_DICT)
    except Exception as exc:
        raise InvalidEquationError(f"Função inválida: {expr}") from exc

    if X not in parsed.free_symbols:
        raise InvalidEquationError("A função precisa depender de x")

    return parsed


def _solve_domain(expr: str, show_steps: bool) -> tuple[str, list[StepResult]]:
    parsed = _parse_function(expr)
    domain = continuous_domain(parsed, X, S.Reals)
    result = f"Domínio: { _format_set(domain) }"
    steps = [StepResult(rule="Analisa restrições de denominador, raiz e log", before=expr, after=result)]
    return result, steps if show_steps else []


def _solve_extrema(expr: str, show_steps: bool) -> tuple[str, list[StepResult]]:
    parsed = _parse_function(expr)
    derivative = diff(parsed, X)
    critical_points = solveset(Eq(derivative, 0), X, domain=S.Reals)

    if not critical_points.is_FiniteSet:
        raise InvalidEquationError("Não foi possível determinar extremos automaticamente para essa função")

    analyses = []
    second_derivative = diff(parsed, X, 2)
    for point in critical_points:
        value = parsed.subs(X, point)
        curvature = second_derivative.subs(X, point)
        if curvature.is_real and curvature > 0:
            kind = "mínimo local"
        elif curvature.is_real and curvature < 0:
            kind = "máximo local"
        else:
            kind = "ponto crítico"
        analyses.append(f"{kind} em x = {_format_number(point)} com y = {_format_number(value)}")

    result = "Extremos: " + "; ".join(analyses)
    steps = [
        StepResult(rule="Deriva a função", before=expr, after=f"f'(x) = {derivative}"),
        StepResult(rule="Resolve f'(x) = 0", before=f"f'(x) = {derivative}", after=result),
    ]
    return result, steps if show_steps else []


def _solve_intersection(expr: str, show_steps: bool) -> tuple[str, list[StepResult]]:
    before = expr
    expr = expr.strip()

    other_expr = None
    if " with " in expr.lower():
        left, right = re.split(r"\s+with\s+", expr, maxsplit=1, flags=re.IGNORECASE)
        expr = left.strip()
        other_expr = right.strip()
    elif " and " in expr.lower():
        left, right = re.split(r"\s+and\s+", expr, maxsplit=1, flags=re.IGNORECASE)
        expr = left.strip()
        other_expr = right.strip()

    parsed = _parse_function(expr)

    if other_expr:
        other_parsed = _parse_function(other_expr)
        solutions = solveset(Eq(parsed, other_parsed), X, domain=S.Reals)
        if not solutions.is_FiniteSet:
            raise InvalidEquationError("Não foi possível calcular a interseção automaticamente")
        points = [f"({_format_number(point)}, {_format_number(parsed.subs(X, point))})" for point in solutions]
        result = "Interseções: " + ", ".join(points)
        steps = [StepResult(rule="Iguala as funções", before=before, after=f"{parsed} = {other_parsed}"), StepResult(rule="Resolve a equação resultante", before=f"{parsed} = {other_parsed}", after=result)]
        return result, steps if show_steps else []

    roots = solveset(Eq(parsed, 0), X, domain=S.Reals)
    if roots.is_FiniteSet:
        root_text = ", ".join(f"x = {_format_number(root)}" for root in roots)
        result = f"Interseções com o eixo x: {root_text}"
    else:
        result = "Interseções com o eixo x: não determinadas automaticamente"

    y_intercept = parsed.subs(X, 0)
    if y_intercept.is_real:
        result += f"; eixo y em (0, {_format_number(y_intercept)})"

    steps = [StepResult(rule="Resolve f(x) = 0", before=expr, after=result)]
    return result, steps if show_steps else []


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
    try:
        numeric = float(value)
    except Exception:
        return str(value)
    if numeric.is_integer():
        return str(int(numeric))
    return (f"{numeric:.10f}").rstrip("0").rstrip(".")