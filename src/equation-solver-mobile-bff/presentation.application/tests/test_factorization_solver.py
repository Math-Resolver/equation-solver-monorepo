from pathlib import Path
import sys
import unittest


APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from domain.equations.errors import InvalidEquationError
from domain.equations.strategies.factorization_solver import solve_factorization


class SolveFactorizationTests(unittest.TestCase):
    def test_factorizes_simple_number(self) -> None:
        result = solve_factorization("2", show_steps=False)
        self.assertEqual(result.result, "2")

    def test_factorizes_composite_number(self) -> None:
        result = solve_factorization("12", show_steps=False)
        self.assertEqual(result.result, "2^2 × 3")

    def test_factorizes_number_with_fator_function(self) -> None:
        result = solve_factorization("fator(60)", show_steps=False)
        self.assertEqual(result.result, "2^2 × 3 × 5")

    def test_factorizes_number_with_factorize_function(self) -> None:
        result = solve_factorization("factorize(60)", show_steps=False)
        self.assertEqual(result.result, "2^2 × 3 × 5")

    def test_factorizes_with_steps(self) -> None:
        result = solve_factorization("12", show_steps=True)
        self.assertEqual(result.result, "2^2 × 3")
        self.assertGreater(len(result.steps), 0)
        self.assertIn("×", result.steps[-1].after)

    def test_factorizes_prime_number(self) -> None:
        result = solve_factorization("7", show_steps=False)
        self.assertEqual(result.result, "7")

    def test_factorizes_power_of_two(self) -> None:
        result = solve_factorization("8", show_steps=False)
        self.assertEqual(result.result, "2^3")

    def test_factorizes_large_number(self) -> None:
        result = solve_factorization("100", show_steps=False)
        self.assertEqual(result.result, "2^2 × 5^2")

    def test_rejects_number_less_than_two(self) -> None:
        with self.assertRaises(InvalidEquationError):
            solve_factorization("1", show_steps=False)

    def test_rejects_negative_number(self) -> None:
        with self.assertRaises(InvalidEquationError):
            solve_factorization("-5", show_steps=False)

    def test_rejects_invalid_number(self) -> None:
        with self.assertRaises(InvalidEquationError):
            solve_factorization("abc", show_steps=False)

    def test_factorizes_number_from_fator_with_spaces(self) -> None:
        result = solve_factorization("fator( 30 )", show_steps=False)
        self.assertEqual(result.result, "2 × 3 × 5")


if __name__ == "__main__":
    unittest.main()
