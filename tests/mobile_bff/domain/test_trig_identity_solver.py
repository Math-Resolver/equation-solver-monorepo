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

from domain.equations.strategies.trig_identity_solver import solve_prove


class SolveTrigIdentityTests(unittest.TestCase):
    def test_prove_trig_identity_true(self) -> None:
        result = solve_prove("prove: sin(x)**2 + cos(x)**2 = 1", show_steps=True)
        self.assertEqual(result.result, "Equivalent")
        self.assertGreater(len(result.steps), 0)

    def test_prove_trig_identity_false(self) -> None:
        result = solve_prove("prove: sin(x) = cos(x)", show_steps=False)
        self.assertTrue(result.result.startswith("Not equivalent"))


if __name__ == "__main__":
    unittest.main()
