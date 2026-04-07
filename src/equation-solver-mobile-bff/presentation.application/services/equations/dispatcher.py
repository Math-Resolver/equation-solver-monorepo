from services.equations.equation_type_detector import EquationType
from services.equations.errors import UnsupportedEquationTypeError
from services.equations.parser import ParsedEquation
from services.solvers.linear import solve_linear
from services.solvers.models import SolveResult
from services.solvers.quadratic import solve_quadratic
from services.solvers.system import solve_system


def dispatch_solver(parsed: ParsedEquation, equation_type: EquationType, show_steps: bool) -> SolveResult:
    if equation_type == EquationType.LINEAR:
        return solve_linear(parsed.equations[0], show_steps=show_steps)

    if equation_type == EquationType.QUADRATIC:
        return solve_quadratic(parsed.equations[0], show_steps=show_steps)

    if equation_type == EquationType.SYSTEM:
        return solve_system(parsed.equations, show_steps=show_steps)

    raise UnsupportedEquationTypeError("Tipo de equação não suportada para resolução")
