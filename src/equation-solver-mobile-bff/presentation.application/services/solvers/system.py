from services.equations.errors import UnsupportedEquationTypeError
from services.solvers.models import SolveResult
from services.solvers.strategy import EquationSolverStrategy


class SystemSolverStrategy(EquationSolverStrategy):
    """Strategy for solving system of equations."""

    def solve(self, equations: list[str], show_steps: bool) -> SolveResult:
        return solve_system(equations, show_steps)


def solve_system(equations: list[str], show_steps: bool) -> SolveResult:
    raise UnsupportedEquationTypeError("System solver is not implemented yet")
