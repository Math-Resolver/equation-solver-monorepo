from math import pi, sqrt
import re

from domain.equations.strategies.models.models_solver import SolveResult, StepResult
from domain.equations.strategies.strategy_solver import EquationSolverStrategy


class GeometrySolverStrategy(EquationSolverStrategy):
    def solve(self, equation: str, show_steps: bool) -> SolveResult:
        return solve_geometry(equation, show_steps)


def solve_geometry(equation: str, show_steps: bool) -> SolveResult:
    parts = equation.split(":", 1)
    if len(parts) != 2:
        return _error("Formato de geometria inválido. Use 'area:' ou 'perimeter:'.")

    operation, payload = parts[0].strip().lower(), parts[1].strip()
    
    match = re.match(r"^(circle|rectangle|triangle)\b\s*(.*)", payload, re.IGNORECASE)
    if not match:
        return _error("Operação de geometria desconhecida")
        
    shape, args_str = match.groups()
    
    handlers = {
        "area": {
            "circle": _area_circle,
            "rectangle": _area_rectangle,
            "triangle": _area_triangle,
        },
        "perimeter": {
            "circle": _perimeter_circle,
            "rectangle": _perimeter_rectangle,
            "triangle": _perimeter_triangle,
        }
    }
    
    handler = handlers.get(operation, {}).get(shape.lower())
    return handler(equation, args_str, show_steps) if handler else _error("Operação de geometria desconhecida")


def _error(message: str) -> SolveResult:
    return SolveResult(result="", steps=[], error=message)


def _build_result(value: float, rule: str, equation: str, show_steps: bool) -> SolveResult:
    result_str = str(round(value, 6))
    steps = [StepResult(rule=rule, before=equation, after=result_str)] if show_steps else []
    return SolveResult(result=result_str, steps=steps)


def _extract_args(args_str: str) -> list[float]:
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", args_str)]


def _area_circle(eq: str, args: str, show: bool) -> SolveResult:
    nums = _extract_args(args)
    return _build_result(pi * nums[0]**2, "Area do círculo", eq, show) if nums else \
           _error("Formato: 'area:circle r'")


def _area_rectangle(eq: str, args: str, show: bool) -> SolveResult:
    nums = _extract_args(args)
    return _build_result(nums[0] * nums[1], "Area do retângulo", eq, show) if len(nums) >= 2 else \
           _error("Formato: 'area:rectangle w,h'")


def _area_triangle(eq: str, args: str, show: bool) -> SolveResult:
    nums = _extract_args(args)
    if len(nums) == 3:
        s = sum(nums) / 2.0
        area = sqrt(max(0.0, s * (s - nums[0]) * (s - nums[1]) * (s - nums[2])))
        return _build_result(area, "Area do triângulo (Heron)", eq, show)
    if len(nums) >= 2:
        return _build_result(0.5 * nums[0] * nums[1], "Area do triângulo (base/altura)", eq, show)
    return _error("Operação de geometria desconhecida")


def _perimeter_circle(eq: str, args: str, show: bool) -> SolveResult:
    nums = _extract_args(args)
    return _build_result(2 * pi * nums[0], "Perímetro do círculo", eq, show) if nums else \
           _error("Formato: 'perimeter:circle r'")


def _perimeter_rectangle(eq: str, args: str, show: bool) -> SolveResult:
    nums = _extract_args(args)
    return _build_result(2 * (nums[0] + nums[1]), "Perímetro do retângulo", eq, show) if len(nums) >= 2 else \
           _error("Formato: 'perimeter:rectangle w,h'")


def _perimeter_triangle(eq: str, args: str, show: bool) -> SolveResult:
    nums = _extract_args(args)
    return _build_result(sum(nums[:3]), "Perímetro do triângulo", eq, show) if len(nums) >= 3 else \
           _error("Operação de geometria desconhecida")