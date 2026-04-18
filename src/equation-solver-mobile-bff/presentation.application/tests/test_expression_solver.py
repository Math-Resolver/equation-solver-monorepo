from pathlib import Path
import sys
import unittest


APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from services.equations.errors import InvalidEquationError
from services.solvers.expression import solve_expression


class SolveExpressionTests(unittest.TestCase):
    def test_solves_simple_expression_with_steps(self) -> None:
        result = solve_expression("2+2", show_steps=True)

        self.assertEqual(result.result, "4")
        self.assertEqual(len(result.steps), 1)
        self.assertEqual(result.steps[0].before, "2+2")
        self.assertEqual(result.steps[0].after, "4")

    def test_honors_operator_precedence_in_steps(self) -> None:
        result = solve_expression("2+2*5", show_steps=True)

        self.assertEqual(result.result, "12")
        self.assertEqual(len(result.steps), 2)
        self.assertEqual(result.steps[0].before, "2+2*5")
        self.assertEqual(result.steps[0].after, "2+10")
        self.assertEqual(result.steps[1].before, "2+10")
        self.assertEqual(result.steps[1].after, "12")

    def test_rejects_invalid_characters(self) -> None:
        with self.assertRaises(InvalidEquationError):
            solve_expression("2+2;import os", show_steps=False)


if __name__ == "__main__":
    unittest.main()