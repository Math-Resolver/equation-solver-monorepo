import re

from services.equations.errors import InvalidEquationError
from services.solvers.models import SolveResult, StepResult
from services.solvers.strategy import EquationSolverStrategy


class ExpressionSolverStrategy(EquationSolverStrategy):
    """Strategy for evaluating simple arithmetic expressions."""

    def solve(self, expression: str, show_steps: bool) -> SolveResult:
        return solve_expression(expression, show_steps)


def solve_expression(expression: str, show_steps: bool) -> SolveResult:
    normalized = expression.strip()
    _validate_expression_safety(normalized)

    result_value = eval(normalized)
    result_text = str(int(result_value) if isinstance(result_value, float) and result_value.is_integer() else result_value)

    if not show_steps:
        return SolveResult(result=result_text, steps=[])

    steps = _generate_resolution_steps(normalized, result_text)
    return SolveResult(result=result_text, steps=steps)


def _generate_resolution_steps(expression: str, final_result: str) -> list[StepResult]:
    steps = []
    current = expression
    
    while current != final_result:
        next_operation = _find_and_evaluate_next_operation(current)
        
        if not next_operation:
            break
        
        operation_expr, operation_result = next_operation
        steps.append(
            StepResult(
                rule=f"Calcula {operation_expr}",
                before=current,
                after=operation_result,
            )
        )
        current = operation_result
    
    if not steps:
        steps.append(
            StepResult(
                rule="Resultado da expressão",
                before=expression,
                after=final_result,
            )
        )
    
    return steps


def _find_and_evaluate_next_operation(expression: str) -> tuple[str, str] | None:
    operations_order = [
        (r"\d+(?:\.\d+)?\s*\*\s*\d+(?:\.\d+)?", "*"),
        (r"\d+(?:\.\d+)?\s*/\s*\d+(?:\.\d+)?", "/"),
        (r"\d+(?:\.\d+)?\s*\+\s*\d+(?:\.\d+)?", "+"),
        (r"\d+(?:\.\d+)?\s*-\s*\d+(?:\.\d+)?", "-"),
    ]
    
    for pattern, _ in operations_order:
        match = re.search(pattern, expression)
        if match:
            operation_expr = match.group(0)
            operation_result = eval(operation_expr)
            result_str = str(int(operation_result) if isinstance(operation_result, float) and operation_result.is_integer() else operation_result)
            new_expression = expression[:match.start()] + result_str + expression[match.end():]
            return operation_expr, new_expression
    
    return None


def _validate_expression_safety(expression: str) -> None:
    allowed_chars = set("0123456789+-*/(). ")
    if not all(c in allowed_chars for c in expression):
        raise InvalidEquationError(f"Expressão contém caracteres inválidos: '{expression}'")
