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

from domain.equations.equation_type_detector import EquationType, detect_equation_type
from domain.equations.parser import ParsedEquation


class DetectEquationTypeTests(unittest.TestCase):
    def test_detects_system(self) -> None:
        parsed = ParsedEquation(raw="x=1\ny=2", equations=["x=1", "y=2"])

        self.assertEqual(detect_equation_type(parsed), EquationType.SYSTEM)

    def test_detects_quadratic(self) -> None:
        parsed = ParsedEquation(raw="x^2+5=0", equations=["x^2+5=0"])

        self.assertEqual(detect_equation_type(parsed), EquationType.QUADRATIC)

    def test_detects_linear(self) -> None:
        parsed = ParsedEquation(raw="2x+5=15", equations=["2x+5=15"])

        self.assertEqual(detect_equation_type(parsed), EquationType.LINEAR)

    def test_detects_expression(self) -> None:
        parsed = ParsedEquation(raw="2+2*5", equations=["2+2*5"])

        self.assertEqual(detect_equation_type(parsed), EquationType.EXPRESSION)

    def test_detects_statistics(self) -> None:
        parsed = ParsedEquation(raw="media: 1, 2, 3", equations=["media: 1, 2, 3"])

        self.assertEqual(detect_equation_type(parsed), EquationType.STATISTICS)


if __name__ == "__main__":
    unittest.main()