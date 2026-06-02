import cmath

from domain.equations.strategies.models.models_solver import SolveResult, StepResult
from domain.equations.strategies.strategy_solver import EquationSolverStrategy


class QuadraticSolverStrategy(EquationSolverStrategy):
    def solve(self, equation: str, show_steps: bool) -> SolveResult:
        return solve_quadratic(equation, show_steps)


def solve_quadratic(equation: str, show_steps: bool) -> SolveResult:
    parsed, parse_error = _parse_quadratic_equation(equation.replace(" ", ""))
    if parse_error:
        return SolveResult(result="", steps=[], error=parse_error)

    a, b, c = parsed
    if abs(a) < 1e-12:
        return SolveResult(result="", steps=[], error="Equação do segundo grau deve ter coeficiente a diferente de zero")

    delta = (b * b) - (4 * a * c)
    sqrt_delta, denominator = cmath.sqrt(delta), 2 * a
    x1, x2 = (-b + sqrt_delta) / denominator, (-b - sqrt_delta) / denominator
    
    result_text = f"x1 = {_format_number(x1)}, x2 = {_format_number(x2)}"
    graph = _build_quadratic_graph(a, b, c, x1, x2)

    steps = [
        StepResult(rule="Identifica os coeficientes da equação", before=equation, after=f"a = {_format_number(a)}, b = {_format_number(b)}, c = {_format_number(c)}"),
        StepResult(rule="Calcula o discriminante", before=f"Δ = b² - 4ac = {_format_number(b)}² - 4·{_format_number(a)}·{_format_number(c)}", after=f"Δ = {_format_number(delta)}"),
        StepResult(rule="Aplica a fórmula de Bhaskara", before="x = (-b ± √Δ) / 2a", after=result_text),
    ] if show_steps else []

    return SolveResult(result=result_text, steps=steps, graph=graph)


def _build_quadratic_graph(a: float, b: float, c: float, x1: complex, x2: complex) -> dict:
    vx = -b / (2 * a)
    real_roots = [float(r.real) for r in (x1, x2) if abs(r.imag) < 1e-12]
    bounds = real_roots + [float(vx)]
    
    left_bound, right_bound = (min(bounds) - 2.0, max(bounds) + 2.0) if real_roots else (float(vx) - 2.5, float(vx) + 2.5)
    span = right_bound - left_bound
    xs = [left_bound + i * (span / 24) for i in range(25)]

    return {
        "kind": "quadratic",
        "expression": _format_quadratic_expression(a, b, c),
        "coefficients": {"a": float(a), "b": float(b), "c": float(c)},
        "roots": [_format_number(x1), _format_number(x2)],
        "vertex": {"x": float(vx), "y": float((a * vx * vx) + (b * vx) + c)},
        "samplePoints": [{"x": float(round(x, 3)), "y": float(round((a * x * x) + (b * x) + c, 3))} for x in xs],
    }


def _format_quadratic_expression(a: float, b: float, c: float) -> str:
    parts = []
    for val, suffix in ((a, "x^2"), (b, "x"), (c, "")):
        if abs(val) > 1e-12 or (not suffix and not parts):
            parts.append(_format_signed_term(val, suffix, not parts))
    return f"f(x) = {' '.join(parts)}"


def _format_signed_term(value: float, suffix: str, first: bool) -> str:
    mag = _format_number(abs(value))
    term = suffix if suffix and mag == "1" else f"{mag}{suffix}"
    return (term if value >= 0 else f"-{term}") if first else (f"+ {term}" if value >= 0 else f"- {term}")


def _parse_quadratic_equation(equation: str) -> tuple[tuple[float, float, float] | None, str | None]:
    parts = equation.split("=", 1)
    if len(parts) != 2:
        return None, "Equação do segundo grau deve conter '='"

    l_side, l_err = _parse_quadratic_side(parts[0])
    r_side, r_err = _parse_quadratic_side(parts[1])
    
    return ((l_side[0] - r_side[0], l_side[1] - r_side[1], l_side[2] - r_side[2]), None) if not (l_err or r_err) else (None, l_err or r_err)


def _parse_quadratic_side(expression: str) -> tuple[tuple[float, float, float] | None, str | None]:
    normalized = expression.replace("**", "^").replace("-", "+-").lstrip("+")
    if not normalized:
        return (0.0, 0.0, 0.0), None

    coeffs = {"x^2": 0.0, "x": 0.0, "c": 0.0}
    for term in (p for p in normalized.split("+") if p):
        kind = "x^2" if "x^2" in term else "x" if "x" in term else "c"
        
        if kind == "c":
            if not _is_number(term):
                return None, f"Formato inválido na expressão: '{expression}'"
            coeffs["c"] += float(term)
        else:
            prefix = term.split(kind, 1)[0].replace("*", "")
            coeffs[kind] += -1.0 if prefix == "-" else 1.0 if prefix in ("", "+") else float(prefix)

    return (coeffs["x^2"], coeffs["x"], coeffs["c"]), None


def _format_number(value: complex | float) -> str:
    if isinstance(value, complex):
        if abs(value.imag) < 1e-12:
            return _format_number(value.real)
        return f"{_format_number(value.real)} {'+' if value.imag >= 0 else '-'} {_format_number(abs(value.imag))}i"

    rounded = round(float(value), 10)
    return str(int(rounded)) if rounded.is_integer() else f"{rounded:.10f}".rstrip("0").rstrip(".")


def _is_number(text: str) -> bool:
    return bool(text) and text.strip().lstrip("+-").replace(".", "", 1).isdigit()