from abc import ABC, abstractmethod

from domain.equations.strategies.models.models_solver import SolveResult


class EquationSolverStrategy(ABC):
    """Base strategy class for equation solvers."""

    @abstractmethod
    def solve(self, equation_data, show_steps: bool) -> SolveResult:
        """
        Solve an equation.

        Args:
            equation_data: The equation(s) to solve (str for single, list[str] for system)
            show_steps: Whether to include solution steps

        Returns:
            SolveResult: The solution with optional steps
        """
        pass
