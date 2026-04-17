from services.equations.errors import UnsupportedEquationTypeError
from services.solvers.models import SolveResult
from services.solvers.strategy import EquationSolverStrategy


class QuadraticSolverStrategy(EquationSolverStrategy):
    """Strategy for solving quadratic equations."""

    def solve(self, equation: str, show_steps: bool) -> SolveResult:
        return solve_quadratic(equation, show_steps)


def solve_quadratic(equation: str, show_steps: bool) -> SolveResult:
    raise UnsupportedEquationTypeError("Quadratic solver is not implemented yet")
