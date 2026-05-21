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

from domain.equations.strategies.linear_solver import solve_linear


class SolveLinearTests(unittest.TestCase):
    def test_solves_linear_equation_with_steps(self) -> None:
        result = solve_linear("2*x+5=15", show_steps=True)

        self.assertEqual(result.result, "x = 5")
        self.assertEqual(len(result.steps), 2)
        self.assertEqual(result.steps[0].before, "2x + 5 = 15")
        self.assertEqual(result.steps[0].after, "2x = 10")
        self.assertEqual(result.steps[1].after, "x = 5")

    def test_rejects_invalid_linear_format(self) -> None:
        result = solve_linear("2 + 2", show_steps=False)
        self.assertIsNotNone(result.error)

    def test_rejects_zero_coefficient(self) -> None:
        result = solve_linear("0x+5=15", show_steps=False)
        self.assertIsNotNone(result.error)


if __name__ == "__main__":
    unittest.main()