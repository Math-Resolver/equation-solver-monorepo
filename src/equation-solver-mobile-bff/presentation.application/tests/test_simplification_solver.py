from pathlib import Path
import sys
import unittest


APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from domain.equations.errors import InvalidEquationError
from domain.equations.strategies.simplification_solver import solve_simplification


class SolveSimplificationTests(unittest.TestCase):
    def test_simplifies_like_terms(self) -> None:
        result = solve_simplification("2x + 3x", show_steps=False)

        self.assertEqual(result.result, "5x")

    def test_simplifies_mixed_terms(self) -> None:
        result = solve_simplification("2x + 5 + 3x + 2", show_steps=False)

        self.assertEqual(result.result, "5x+7")

    def test_simplifies_with_negative_coefficients(self) -> None:
        result = solve_simplification("5x - 2x + 3", show_steps=False)

        self.assertEqual(result.result, "3x+3")

    def test_simplifies_with_steps(self) -> None:
        result = solve_simplification("4x + 2x", show_steps=True)

        self.assertEqual(result.result, "6x")
        self.assertGreater(len(result.steps), 0)

    def test_rejects_expression_without_variables(self) -> None:
        with self.assertRaises(InvalidEquationError):
            solve_simplification("2 + 3", show_steps=False)

    def test_simplifies_with_multiple_variables(self) -> None:
        pass

    def test_simplifies_polynomial_expression(self) -> None:
        pass


if __name__ == "__main__":
    unittest.main()
