from domain.equations.equation_type_detector import EquationType
from domain.equations.errors import InvalidEquationError
from domain.equations.parser import ParsedEquation
from domain.equations.strategies.expression_solver import ExpressionSolverStrategy
from domain.equations.strategies.factorization_solver import FactorizationSolverStrategy
from domain.equations.strategies.fractions_solver import FractionSolverStrategy
from domain.equations.strategies.function_analysis_solver import FunctionAnalysisSolverStrategy
from domain.equations.strategies.inequality_solver import InequalitySolverStrategy
from domain.equations.strategies.linear_solver import LinearSolverStrategy
from domain.equations.strategies.models.models_solver import SolveResult
from domain.equations.strategies.quadratic_solver import QuadraticSolverStrategy
from domain.equations.strategies.simplification_solver import SimplificationSolverStrategy
from domain.equations.strategies.system_solver import SystemSolverStrategy


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


def is_supported_equation_type(equation_type: object) -> bool:
    return equation_type in SOLVER_STRATEGIES


def dispatch_solver(parsed: ParsedEquation, equation_type: EquationType, show_steps: bool) -> SolveResult:
    """
    Dispatch to appropriate solver strategy based on equation type.

    Args:
        parsed: The parsed equation data
        equation_type: The detected equation type
        show_steps: Whether to include solution steps

    Returns:
        SolveResult: The solution result

    """
    strategy = SOLVER_STRATEGIES[equation_type]
    
    if equation_type == EquationType.SYSTEM:
        equation_data = parsed.equations
    else:
        equation_data = parsed.equations[0]
    
    return strategy.solve(equation_data, show_steps=show_steps)


def dispatch_solver_safe(
    parsed: ParsedEquation,
    equation_type: EquationType,
    show_steps: bool,
) -> tuple[SolveResult | None, str | None]:
    try:
        result = dispatch_solver(parsed=parsed, equation_type=equation_type, show_steps=show_steps)
        return result, None
    except InvalidEquationError as exc:
        return None, str(exc)
