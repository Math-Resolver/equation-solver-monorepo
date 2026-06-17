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

from domain.equations.strategies.quadratic_solver import solve_quadratic


class SolveQuadraticTests(unittest.TestCase):
    def test_solves_quadratic_equation(self) -> None:
        result = solve_quadratic("x^2-5x+6=0", show_steps=False)

        self.assertEqual(result.result, "x1 = 3, x2 = 2")
        self.assertIsNotNone(result.graph)
        self.assertEqual(result.graph["kind"], "quadratic")
        self.assertEqual(result.graph["coefficients"], {"a": 1.0, "b": -5.0, "c": 6.0})

    def test_solves_quadratic_equation_with_steps(self) -> None:
        result = solve_quadratic("x^2-4=0", show_steps=True)

        self.assertEqual(result.result, "x1 = 2, x2 = -2")
        self.assertEqual(len(result.steps), 3)
        self.assertIsNotNone(result.graph)

    def test_rejects_equation_without_equals_sign(self) -> None:
        result = solve_quadratic("x^2-5x+6", show_steps=False)
        self.assertIsNotNone(result.error)


if __name__ == "__main__":
    unittest.main()
