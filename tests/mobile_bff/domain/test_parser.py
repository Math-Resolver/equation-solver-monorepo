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

from domain.equations.parser import parse_equation_input


class ParseEquationInputTests(unittest.TestCase):
    def test_trims_input_and_splits_equations(self) -> None:
        parsed, err = parse_equation_input(" 2 + 2\n3 + 3, 4 + 4 ")

        self.assertIsNone(err)
        self.assertEqual(parsed.raw, "2 + 2\n3 + 3, 4 + 4")
        self.assertEqual(parsed.equations, ["2 + 2", "3 + 3", "4 + 4"])

    def test_accepts_simple_expression(self) -> None:
        parsed, err = parse_equation_input("2 + 2")

        self.assertIsNone(err)
        self.assertEqual(parsed.equations, ["2 + 2"])

    def test_accepts_statistics_request_as_single_payload(self) -> None:
        parsed, err = parse_equation_input("media: 1, 2, 3")

        self.assertIsNone(err)
        self.assertEqual(parsed.equations, ["media: 1, 2, 3"])

    def test_rejects_empty_input(self) -> None:
        parsed, err = parse_equation_input("   ")
        self.assertIsNone(parsed)
        self.assertIsNotNone(err)

    def test_rejects_payload_without_equations(self) -> None:
        parsed, err = parse_equation_input(", , \n")
        self.assertIsNone(parsed)
        self.assertIsNotNone(err)


if __name__ == "__main__":
    unittest.main()