from pathlib import Path
import sys
import unittest

from fastapi.testclient import TestClient


APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from main import app


class SolveEquationRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_solves_simple_expression(self) -> None:
        response = self.client.post(
            "/v1/equation/solve",
            json={"equation": "2+2*5", "showSteps": True},
        )

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["result"], "12")
        self.assertEqual(len(body["steps"]), 2)
        self.assertEqual(body["steps"][0]["before"], "2+2*5")
        self.assertEqual(body["steps"][0]["after"], "2+10")
        self.assertEqual(body["steps"][1]["after"], "12")

    def test_rejects_empty_equation(self) -> None:
        response = self.client.post(
            "/v1/equation/solve",
            json={"equation": "   ", "showSteps": True},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "A equação não pode ser vazia")


if __name__ == "__main__":
    unittest.main()