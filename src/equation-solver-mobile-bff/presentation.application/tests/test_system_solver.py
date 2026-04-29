from pathlib import Path
import sys
import unittest


APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from services.equations.errors import InvalidEquationError
from services.solvers.system import solve_system


class SolveSystemTests(unittest.TestCase):
    def test_solves_two_equation_system(self) -> None:
        result = solve_system(["x+y=5", "x-y=1"], show_steps=False)

        self.assertEqual(result.result, "x = 3, y = 2")

    def test_solves_two_equation_system_with_steps(self) -> None:
        result = solve_system(["2x+y=8", "x-y=1"], show_steps=True)

        self.assertEqual(result.result, "x = 3, y = 2")
        self.assertEqual(len(result.steps), 3)

    def test_rejects_system_with_wrong_number_of_equations(self) -> None:
        with self.assertRaises(InvalidEquationError):
            solve_system(["x+y=5"], show_steps=False)


if __name__ == "__main__":
    unittest.main()
