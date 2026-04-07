from services.equations.errors import UnsupportedEquationTypeError
from services.solvers.models import SolveResult


def solve_quadratic(equation: str, show_steps: bool) -> SolveResult:
    raise UnsupportedEquationTypeError("Quadratic solver is not implemented yet")
