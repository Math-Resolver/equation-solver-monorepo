from pathlib import Path
import sys
import unittest


APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from services.equations.errors import InvalidEquationError
from services.solvers.fractions import solve_fraction


class SolveFractionTests(unittest.TestCase):
    def test_solves_simple_fraction_addition(self) -> None:
        result = solve_fraction("1/2 + 1/2", show_steps=False)
        self.assertEqual(result.result, "1")

    def test_solves_fraction_addition_with_different_denominators(self) -> None:
        result = solve_fraction("1/2 + 1/3", show_steps=False)
        self.assertEqual(result.result, "5/6")

    def test_solves_fraction_subtraction(self) -> None:
        result = solve_fraction("3/4 - 1/4", show_steps=False)
        self.assertEqual(result.result, "1/2")

    def test_solves_fraction_multiplication(self) -> None:
        result = solve_fraction("2/3 * 3/4", show_steps=False)
        self.assertEqual(result.result, "1/2")

    def test_solves_fraction_division(self) -> None:
        result = solve_fraction("1/2 / 1/4", show_steps=False)
        self.assertEqual(result.result, "2")

    def test_solves_fraction_with_steps(self) -> None:
        result = solve_fraction("1/2 + 1/3", show_steps=True)
        self.assertEqual(result.result, "5/6")
        self.assertGreater(len(result.steps), 0)

    def test_simplifies_fractions(self) -> None:
        result = solve_fraction("2/4", show_steps=False)
        self.assertEqual(result.result, "1/2")

    def test_solves_mixed_fraction_arithmetic(self) -> None:
        result = solve_fraction("1/2 + 1/3 - 1/6", show_steps=False)
        self.assertEqual(result.result, "2/3")

    def test_solves_fraction_with_whole_numbers(self) -> None:
        result = solve_fraction("2 + 1/2", show_steps=False)
        self.assertEqual(result.result, "5/2")

    def test_rejects_invalid_fraction_format(self) -> None:
        with self.assertRaises(InvalidEquationError):
            solve_fraction("1//2", show_steps=False)


if __name__ == "__main__":
    unittest.main()
