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

from domain.equations.strategies.function_analysis_solver import solve_function_analysis


class SolveFunctionAnalysisTests(unittest.TestCase):
    def test_solves_domain_with_denominator_restriction(self) -> None:
        result = solve_function_analysis("domain: 1/(x-2)", show_steps=True)

        self.assertIn("Domínio:", result.result)
        self.assertIn("2", result.result)
        self.assertGreater(len(result.steps), 0)

    def test_solves_quadratic_extrema(self) -> None:
        result = solve_function_analysis("extrema: x^2 - 4x + 3", show_steps=False)

        self.assertIn("mínimo", result.result.lower())
        self.assertIn("x = 2", result.result)
        self.assertIn("y = -1", result.result)

    def test_solves_intersection_with_x_axis(self) -> None:
        result = solve_function_analysis("intersect: x^2 - 5x + 6", show_steps=False)

        self.assertIn("x = 2", result.result)
        self.assertIn("x = 3", result.result)

    def test_solves_intersection_between_two_functions(self) -> None:
        result = solve_function_analysis("intersect: x + 2 with x^2", show_steps=True)

        self.assertIn("Interseções:", result.result)
        self.assertGreater(len(result.steps), 0)

    def test_rejects_expression_without_analysis_keyword(self) -> None:
        result = solve_function_analysis("x^2 + 1", show_steps=False)
        self.assertIsNotNone(result.error)


if __name__ == "__main__":
    unittest.main()