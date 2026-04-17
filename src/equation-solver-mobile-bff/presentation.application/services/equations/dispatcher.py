from services.equations.equation_type_detector import EquationType
from services.equations.errors import UnsupportedEquationTypeError
from services.equations.parser import ParsedEquation
from services.solvers.linear import LinearSolverStrategy
from services.solvers.models import SolveResult
from services.solvers.quadratic import QuadraticSolverStrategy
from services.solvers.system import SystemSolverStrategy


# Strategy registry mapping equation types to their solvers
SOLVER_STRATEGIES = {
    EquationType.LINEAR: LinearSolverStrategy(),
    EquationType.QUADRATIC: QuadraticSolverStrategy(),
    EquationType.SYSTEM: SystemSolverStrategy(),
}


def dispatch_solver(parsed: ParsedEquation, equation_type: EquationType, show_steps: bool) -> SolveResult:
    """
    Dispatch to appropriate solver strategy based on equation type.

    Args:
        parsed: The parsed equation data
        equation_type: The detected equation type
        show_steps: Whether to include solution steps

    Returns:
        SolveResult: The solution result

    Raises:
        UnsupportedEquationTypeError: If equation type has no registered strategy
    """
    if equation_type not in SOLVER_STRATEGIES:
        raise UnsupportedEquationTypeError("Tipo de equação não suportada para resolução")

    strategy = SOLVER_STRATEGIES[equation_type]
    equation_data = parsed.equations[0] if equation_type != EquationType.SYSTEM else parsed.equations
    return strategy.solve(equation_data, show_steps=show_steps)
