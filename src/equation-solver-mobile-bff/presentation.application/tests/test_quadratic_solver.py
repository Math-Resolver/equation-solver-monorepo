from pathlib import Path
import sys
import unittest


APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from domain.equations.errors import InvalidEquationError
from domain.equations.strategies.quadratic_solver import solve_quadratic


class SolveQuadraticTests(unittest.TestCase):
    def test_solves_quadratic_equation(self) -> None:
        result = solve_quadratic("x^2-5x+6=0", show_steps=False)

        self.assertEqual(result.result, "x1 = 3, x2 = 2")

    def test_solves_quadratic_equation_with_steps(self) -> None:
        result = solve_quadratic("x^2-4=0", show_steps=True)

        self.assertEqual(result.result, "x1 = 2, x2 = -2")
        self.assertEqual(len(result.steps), 3)

    def test_rejects_equation_without_equals_sign(self) -> None:
        with self.assertRaises(InvalidEquationError):
            solve_quadratic("x^2-5x+6", show_steps=False)


if __name__ == "__main__":
    unittest.main()
