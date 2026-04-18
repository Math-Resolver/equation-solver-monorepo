from pathlib import Path
import sys
import unittest


APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from services.equations.errors import InvalidEquationError
from services.solvers.linear import solve_linear


class SolveLinearTests(unittest.TestCase):
    def test_solves_linear_equation_with_steps(self) -> None:
        result = solve_linear("2*x+5=15", show_steps=True)

        self.assertEqual(result.result, "x = 5")
        self.assertEqual(len(result.steps), 2)
        self.assertEqual(result.steps[0].before, "2x + 5 = 15")
        self.assertEqual(result.steps[0].after, "2x = 10")
        self.assertEqual(result.steps[1].after, "x = 5")

    def test_rejects_invalid_linear_format(self) -> None:
        with self.assertRaises(InvalidEquationError):
            solve_linear("2 + 2", show_steps=False)

    def test_rejects_zero_coefficient(self) -> None:
        with self.assertRaises(InvalidEquationError):
            solve_linear("0x+5=15", show_steps=False)


if __name__ == "__main__":
    unittest.main()