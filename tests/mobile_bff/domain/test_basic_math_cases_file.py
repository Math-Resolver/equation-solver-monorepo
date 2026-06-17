from pathlib import Path
import json
import sys
import unittest

from fastapi.testclient import TestClient


APP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
REPO_SRC = REPO_ROOT / "src" / "presentation.application"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))
if str(REPO_SRC) not in sys.path:
    sys.path.insert(0, str(REPO_SRC))

from main import app 


class BasicMathCasesFileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.cases_path = APP_ROOT / "domain" / "manual" / "basic_math_cases.json"

    def test_all_cases_in_file_match_expected_result(self) -> None:
        with self.cases_path.open("r", encoding="utf-8") as file:
            cases = json.load(file)

        for index, case in enumerate(cases):
            response = self.client.post("/v1/equation/solve", json=case["request"])
            self.assertEqual(
                response.status_code,
                200,
                msg=f"Case {index} failed with status {response.status_code}: {case}",
            )

            body = response.json()
            self.assertEqual(
                body["result"],
                case["expectedResult"],
                msg=f"Case {index} returned unexpected result: {case}",
            )


if __name__ == "__main__":
    unittest.main()
