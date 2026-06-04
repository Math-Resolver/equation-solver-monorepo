import re

from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)
from sympy import Symbol, cos, pi, simplify, sin, tan, trigsimp

from domain.equations.strategies.models.models_solver import SolveResult, StepResult
from domain.equations.strategies.strategy_solver import EquationSolverStrategy


class TrigIdentitySolverStrategy(EquationSolverStrategy):
    def solve(self, equation: str, show_steps: bool) -> SolveResult:
        return solve_prove(equation, show_steps)


X = Symbol("x", real=True)
LOCAL_DICT = {"x": X, "sin": sin, "cos": cos, "tan": tan, "pi": pi}


def _safe_parse(expr_text: str):
    expr_text = expr_text.strip()
    if not re.fullmatch(r"[0-9A-Za-z+\-*/^().,\s]+", expr_text):
        raise ValueError("Expressão contém caracteres inválidos")

    transformations = standard_transformations + (convert_xor, implicit_multiplication_application)
    return parse_expr(expr_text.replace("^", "**"), transformations=transformations, local_dict=LOCAL_DICT)


def solve_prove(equation: str, show_steps: bool) -> SolveResult:
    if ":" not in equation:
        return SolveResult(result="", steps=[], error="Formato inválido. Use 'prove: expr1 = expr2'")
    _, payload = equation.split(":", 1)
    if "=" not in payload:
        return SolveResult(result="", steps=[], error="Formato inválido. Use 'expr1 = expr2'")
    left_text, right_text = payload.split("=", 1)
    left = _safe_parse(left_text)
    right = _safe_parse(right_text)
    diff = simplify(left - right)
    trig = trigsimp(diff)
    equivalent = (trig == 0)
    result_text = "Equivalent" if equivalent else f"Not equivalent: {trig}"
    steps = [StepResult(rule="Simplifica diferença", before=payload.strip(), after=str(trig))]
    return SolveResult(result=result_text, steps=steps if show_steps else [])