import re

from sympy import Eq, Function, Symbol, diff as sym_diff, dsolve, integrate as sym_integrate, limit as sym_limit
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr as parse_expr_fn,
    standard_transformations,
)

from domain.equations.strategies.models.models_solver import SolveResult, StepResult
from domain.equations.strategies.strategy_solver import EquationSolverStrategy


X = Symbol("x")


class CalculusSolverStrategy(EquationSolverStrategy):
    def solve(self, equation: str, show_steps: bool) -> SolveResult:
        return solve_calculus(equation, show_steps)



def _safe_parse(expr_text: str):
    transformations = standard_transformations + (convert_xor, implicit_multiplication_application)
    return parse_expr_fn(expr_text.replace("^", "**"), transformations=transformations, local_dict={"x": X})


def _solve_limit(equation: str, payload: str, show_steps: bool) -> SolveResult:
    if "," not in payload:
        return SolveResult(result="", steps=[], error="Formato para limit: 'limit: expr, point' esperada")

    expr_text, point_text = payload.rsplit(",", 1)
    expr = _safe_parse(expr_text)
    pt = _safe_parse(point_text)
    res = sym_limit(expr, X, pt)
    result_text = f"limit = {res}"
    steps = [StepResult(rule="Calcula limite", before=equation, after=str(res))]
    return SolveResult(result=result_text, steps=steps if show_steps else [])


def _solve_integral(equation: str, payload: str, show_steps: bool) -> SolveResult:
    expr = _safe_parse(payload)
    res = sym_integrate(expr, X)
    result_text = f"∫ = {res} + C"
    steps = [StepResult(rule="Calcula primitiva (integral indefinida)", before=equation, after=str(res) + " + C")]
    return SolveResult(result=result_text, steps=steps if show_steps else [])


def _solve_derivative(equation: str, payload: str, show_steps: bool) -> SolveResult:
    expr = _safe_parse(payload)
    res = sym_diff(expr, X)
    result_text = f"f'(x) = {res}"
    steps = [StepResult(rule="Deriva a função", before=equation, after=str(res))]
    return SolveResult(result=result_text, steps=steps if show_steps else [])


def _solve_ode(equation: str, payload: str, show_steps: bool) -> SolveResult:
    transformations = standard_transformations + (convert_xor, implicit_multiplication_application)
    local = {"x": X, "y": Function("y")}
    expr_text = payload.strip()
    expr_text = expr_text.replace("y''", "Derivative(y(x), x, 2)")
    expr_text = expr_text.replace("y'", "Derivative(y(x), x)")
    expr_text = re.sub(r"(?<![A-Za-z0-9_])y(?!\s*\()", "y(x)", expr_text)

    if "=" in expr_text:
        left_text, right_text = expr_text.split("=", 1)
        left = parse_expr_fn(left_text, transformations=transformations, local_dict=local)
        right = parse_expr_fn(right_text, transformations=transformations, local_dict=local)
        eq = Eq(left, right)
    else:
        expr = parse_expr_fn(expr_text, transformations=transformations, local_dict=local)
        eq = Eq(expr, 0)

    sol = dsolve(eq)
    result_text = f"ode solution: {sol}"
    steps = [StepResult(rule="Resolve EDO simples via dsolve", before=equation, after=str(sol))]
    return SolveResult(result=result_text, steps=steps if show_steps else [])


def solve_calculus(equation: str, show_steps: bool) -> SolveResult:
    lowered = equation.lower()
    if ":" in lowered:
        prefix, payload = equation.split(":", 1)
        prefix = prefix.strip().lower()
        payload = payload.strip()
    else:
        return SolveResult(result="", steps=[], error="Formato de cálculo inválido. Use 'limit:', 'integral:', 'derivative:' ou 'ode:'.")

    handlers = {
        "limit": _solve_limit,
        "integral": _solve_integral,
        "integrate": _solve_integral,
        "derivative": _solve_derivative,
        "deriv": _solve_derivative,
        "ode": _solve_ode,
    }

    handler = handlers.get(prefix)
    if handler is None:
        return SolveResult(result="", steps=[], error="Tipo de cálculo não reconhecido")

    return handler(equation, payload, show_steps)