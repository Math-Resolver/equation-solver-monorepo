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


class SolveCalculusODETests(unittest.TestCase):
    def test_first_order_linear_ode(self) -> None:
        result = solve_calculus("ode: y' - y = 0", show_steps=False)
        self.assertIsNone(result.error)
        self.assertIn("exp(x)", result.result)

    def test_second_order_homogeneous_ode(self) -> None:
        result = solve_calculus("ode: y'' + y = 0", show_steps=False)
        self.assertIsNone(result.error)
        self.assertTrue("sin(x)" in result.result or "cos(x)" in result.result)


if __name__ == "__main__":
    unittest.main()
