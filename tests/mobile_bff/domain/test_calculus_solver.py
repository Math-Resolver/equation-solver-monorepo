from pathlib import Path
import sys
import unittest


APP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
REPO_SRC = REPO_ROOT / "src" / "presentation.application"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))
if str(REPO_SRC) not in sys.path:
    sys.path.insert(0, str(REPO_SRC))

from domain.equations.strategies.calculus_solver import solve_calculus


class SolveCalculusTests(unittest.TestCase):
    def test_limit_sin_over_x(self) -> None:
        result = solve_calculus("limit: sin(x)/x, 0", show_steps=False)
        self.assertEqual(result.result, "limit = 1")

    def test_derivative_polynomial(self) -> None:
        result = solve_calculus("derivative: x^3", show_steps=True)
        self.assertEqual(result.result, "f'(x) = 3*x**2")
        self.assertGreater(len(result.steps), 0)

    def test_integral_simple(self) -> None:
        result = solve_calculus("integral: x", show_steps=False)
        self.assertEqual(result.result, "∫ = x**2/2 + C")


if __name__ == "__main__":
    unittest.main()
