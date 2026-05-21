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

from domain.equations.strategies.expression_solver import solve_expression


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
        result = solve_expression("2+2;import os", show_steps=False)
        self.assertIsNotNone(result.error)

    def test_solves_power_expression(self) -> None:
        result = solve_expression("2^3", show_steps=False)
        self.assertEqual(result.result, "8")

    def test_solves_power_expression_with_steps(self) -> None:
        result = solve_expression("2^3+1", show_steps=True)
        self.assertEqual(result.result, "9")
        self.assertGreater(len(result.steps), 0)

    def test_solves_power_with_asterisk_notation(self) -> None:
        result = solve_expression("2**3", show_steps=False)
        self.assertEqual(result.result, "8")

    def test_solves_sqrt_expression(self) -> None:
        result = solve_expression("sqrt(9)", show_steps=False)
        self.assertEqual(result.result, "3")

    def test_solves_sqrt_expression_with_raiz_notation(self) -> None:
        result = solve_expression("raiz(16)", show_steps=False)
        self.assertEqual(result.result, "4")

    def test_solves_sqrt_with_steps(self) -> None:
        result = solve_expression("sqrt(4)+2", show_steps=True)
        self.assertEqual(result.result, "4")
        self.assertGreater(len(result.steps), 0)

    def test_solves_complex_expression_with_power_and_sqrt(self) -> None:
        result = solve_expression("2^3+sqrt(4)", show_steps=False)
        self.assertEqual(result.result, "10")

    def test_solves_decimal_power(self) -> None:
        result = solve_expression("4^0.5", show_steps=False)
        self.assertEqual(result.result, "2")

    def test_solves_decimal_expression(self) -> None:
        result = solve_expression("1.5+2.5", show_steps=False)
        self.assertEqual(result.result, "4")


if __name__ == "__main__":
    unittest.main()