from domain.equations.equation_type_detector import EquationType
from domain.equations.errors import UnsupportedEquationTypeError
from domain.equations.parser import ParsedEquation
from domain.strategies.expression_solver import ExpressionSolverStrategy
from domain.strategies.factorization_solver import FactorizationSolverStrategy
from domain.strategies.fractions_solver import FractionSolverStrategy
from domain.strategies.function_analysis_solver import FunctionAnalysisSolverStrategy
from domain.strategies.inequality_solver import InequalitySolverStrategy
from domain.strategies.linear_solver import LinearSolverStrategy
from domain.strategies.models_solver import SolveResult
from domain.strategies.quadratic_solver import QuadraticSolverStrategy
from domain.strategies.simplification_solver import SimplificationSolverStrategy
from domain.strategies.system_solver import SystemSolverStrategy


SOLVER_STRATEGIES = {
    EquationType.LINEAR: LinearSolverStrategy(),
    EquationType.QUADRATIC: QuadraticSolverStrategy(),
    EquationType.SYSTEM: SystemSolverStrategy(),
    EquationType.EXPRESSION: ExpressionSolverStrategy(),
    EquationType.FACTORIZATION: FactorizationSolverStrategy(),
    EquationType.FUNCTION_ANALYSIS: FunctionAnalysisSolverStrategy(),
    EquationType.FRACTION: FractionSolverStrategy(),
    EquationType.INEQUALITY: InequalitySolverStrategy(),
    EquationType.SIMPLIFICATION: SimplificationSolverStrategy(),
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
    
    if equation_type == EquationType.SYSTEM:
        equation_data = parsed.equations
    else:
        equation_data = parsed.equations[0]
    
    return strategy.solve(equation_data, show_steps=show_steps)
