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

from domain.equations.strategies.system_solver import solve_system


class SolveSystemTests(unittest.TestCase):
    def test_solves_two_equation_system(self) -> None:
        result = solve_system(["x+y=5", "x-y=1"], show_steps=False)

        self.assertEqual(result.result, "x = 3, y = 2")

    def test_solves_two_equation_system_with_steps(self) -> None:
        result = solve_system(["2x+y=8", "x-y=1"], show_steps=True)

        self.assertEqual(result.result, "x = 3, y = 2")
        self.assertEqual(len(result.steps), 3)

    def test_rejects_system_with_wrong_number_of_equations(self) -> None:
        result = solve_system(["x+y=5"], show_steps=False)
        self.assertIsNotNone(result.error)


if __name__ == "__main__":
    unittest.main()
