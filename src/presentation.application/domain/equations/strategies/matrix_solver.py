import re
from sympy import Matrix

from domain.equations.strategies.models.models_solver import SolveResult, StepResult
from domain.equations.strategies.strategy_solver import EquationSolverStrategy


class MatrixSolverStrategy(EquationSolverStrategy):
    def solve(self, equation: str, show_steps: bool) -> SolveResult:
        return solve_matrix(equation, show_steps)


def solve_matrix(equation: str, show_steps: bool) -> SolveResult:
    parts = equation.split(":", 1)
    if len(parts) != 2:
        return _error("Formato de matrix inválido. Use 'determinant:', 'inverse:', 'matrix:' ou 'solve_matrix:'.")

    operation, payload = parts[0].strip().lower(), parts[1].strip()
    handler = {
        "solve_matrix": _solve_system,
        "determinant": _det,
        "det": _det,
        "inverse": _inv,
        "inv": _inv,
        "matrix": _mat,
    }.get(operation)

    return handler(equation, payload, show_steps) if handler else _error("Operação de matriz desconhecida")


def _error(message: str) -> SolveResult:
    return SolveResult(result="", steps=[], error=message)


def _build_result(value: str, rule: str, equation: str, show_steps: bool) -> SolveResult:
    steps = [StepResult(rule=rule, before=equation, after=value)] if show_steps else []
    return SolveResult(result=value, steps=steps)


def _parse_matrix_payload(payload: str) -> Matrix | None:
    mat = [[float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", r)] for r in payload.split(";") if r.strip()]
    return Matrix(mat) if mat and all(mat) and len(set(len(r) for r in mat)) == 1 else None


def _solve_system(eq: str, payload: str, show: bool) -> SolveResult:
    parts = payload.split("|", 1)
    if len(parts) != 2:
        return _error("Formato inválido para solve_matrix. Use 'solve_matrix: A | b'")

    a_mat = _parse_matrix_payload(parts[0])
    b_temp = _parse_matrix_payload(parts[1]) if ";" in parts[1] else None
    
    nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", parts[1])] if b_temp is None else []
    
    bvec = (
        b_temp if b_temp is not None and b_temp.cols == 1 else
        b_temp.T if b_temp is not None and b_temp.rows == 1 else
        Matrix([[n] for n in nums]) if nums else None
    )

    rules = [
        (a_mat is None, "Matriz A inválida"),
        (bvec is None, "Matriz B inválida"),
        (a_mat is not None and bvec is not None and a_mat.rows != bvec.rows, "Dimensões incompatíveis entre A e b"),
        (a_mat is not None and a_mat.rows != a_mat.cols, "Matriz A não quadrada"),
        (a_mat is not None and a_mat.rows == a_mat.cols and a_mat.det() == 0, "Matriz A singular"),
    ]
    
    error_msg = next((msg for cond, msg in rules if cond), None)
    if error_msg:
        return _error(error_msg)

    sol = ", ".join(
        f"x{i+1} = {int(v) if v.is_integer() else round(v, 6)}" 
        for i, v in enumerate(float(v) for v in a_mat.LUsolve(bvec))
    )
    return _build_result(sol, "Resolve sistema NxN via LU", eq, show)


def _det(eq: str, payload: str, show: bool) -> SolveResult:
    m = _parse_matrix_payload(payload)
    err = "Matriz inválida" if m is None else "Matriz não quadrada" if m.rows != m.cols else None
    return _error(err) if err else _build_result(str(m.det()), "Calcula determinante", eq, show)


def _inv(eq: str, payload: str, show: bool) -> SolveResult:
    m = _parse_matrix_payload(payload)
    err = (
        "Matriz inválida" if m is None else 
        "Matriz não quadrada" if m.rows != m.cols else 
        "Matriz singular (não possui inversa)" if m.det() == 0 else None
    )
    return _error(err) if err else _build_result(str(m.inv()), "Calcula inversa", eq, show)


def _mat(eq: str, payload: str, show: bool) -> SolveResult:
    m = _parse_matrix_payload(payload)
    return _build_result(str(m), "Retorna matriz", eq, show) if m is not None else _error("Matriz inválida")