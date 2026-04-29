from pathlib import Path
import sys
import unittest


APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from services.equations.errors import InvalidEquationError
from services.solvers.inequality import solve_inequality


class SolveInequalityTests(unittest.TestCase):
    def test_solves_simple_inequality_greater_than(self) -> None:
        result = solve_inequality("x + 5 > 10", show_steps=False)

        self.assertEqual(result.result, "x > 5")

    def test_solves_inequality_with_multiplication(self) -> None:
        result = solve_inequality("2x - 3 <= 7", show_steps=False)

        self.assertEqual(result.result, "x <= 5")

    def test_solves_inequality_with_negative_coefficient(self) -> None:
        result = solve_inequality("-x + 4 < 10", show_steps=False)

        self.assertEqual(result.result, "x > -6")

    def test_solves_inequality_with_steps(self) -> None:
        result = solve_inequality("3x + 2 >= 11", show_steps=True)

        self.assertEqual(result.result, "x >= 3")
        self.assertEqual(len(result.steps), 2)

    def test_rejects_inequality_without_operator(self) -> None:
        with self.assertRaises(InvalidEquationError):
            solve_inequality("2x + 5 = 15", show_steps=False)

    def test_rejects_inequality_with_zero_coefficient(self) -> None:
        with self.assertRaises(InvalidEquationError):
            solve_inequality("0*x + 5 > 10", show_steps=False)


if __name__ == "__main__":
    unittest.main()
