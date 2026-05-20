from pathlib import Path
import sys
import unittest


APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from domain.equations.strategies.statistics_solver import solve_statistics


class SolveStatisticsTests(unittest.TestCase):
    def test_solves_mean(self) -> None:
        result = solve_statistics("media: 1, 2, 3, 4", show_steps=False)

        self.assertEqual(result.result, "2.5")
        self.assertIsNone(result.error)

    def test_solves_median_with_steps(self) -> None:
        result = solve_statistics("mediana: 5, 1, 3", show_steps=True)

        self.assertEqual(result.result, "3")
        self.assertGreater(len(result.steps), 0)

    def test_solves_mode(self) -> None:
        result = solve_statistics("moda: 2, 2, 3, 4", show_steps=False)

        self.assertEqual(result.result, "Moda: 2")

    def test_solves_combination(self) -> None:
        result = solve_statistics("combina: 5, 2", show_steps=False)

        self.assertEqual(result.result, "10")

    def test_rejects_invalid_combination_payload(self) -> None:
        result = solve_statistics("combina: 5", show_steps=False)

        self.assertIsNotNone(result.error)


if __name__ == "__main__":
    unittest.main()