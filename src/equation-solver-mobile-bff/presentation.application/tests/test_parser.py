from pathlib import Path
import sys
import unittest


APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from services.equations.errors import InvalidEquationError
from services.equations.parser import parse_equation_input


class ParseEquationInputTests(unittest.TestCase):
    def test_trims_input_and_splits_equations(self) -> None:
        parsed = parse_equation_input(" 2 + 2\n3 + 3, 4 + 4 ")

        self.assertEqual(parsed.raw, "2 + 2\n3 + 3, 4 + 4")
        self.assertEqual(parsed.equations, ["2 + 2", "3 + 3", "4 + 4"])

    def test_accepts_simple_expression(self) -> None:
        parsed = parse_equation_input("2 + 2")

        self.assertEqual(parsed.equations, ["2 + 2"])

    def test_rejects_empty_input(self) -> None:
        with self.assertRaises(InvalidEquationError):
            parse_equation_input("   ")

    def test_rejects_payload_without_equations(self) -> None:
        with self.assertRaises(InvalidEquationError):
            parse_equation_input(", , \n")


if __name__ == "__main__":
    unittest.main()