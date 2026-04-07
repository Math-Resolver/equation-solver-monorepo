from services.equations.errors import UnsupportedEquationTypeError
from services.solvers.models import SolveResult


def solve_system(equations: list[str], show_steps: bool) -> SolveResult:
    raise UnsupportedEquationTypeError("System solver is not implemented yet")
