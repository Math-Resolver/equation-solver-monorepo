from pathlib import Path
import sys
import unittest
from unittest.mock import patch

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

    def test_solves_quadratic_equation(self) -> None:
        response = self.client.post(
            "/v1/equation/solve",
            json={"equation": "x^2-5x+6=0", "showSteps": True},
        )

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["result"], "x1 = 3, x2 = 2")
        self.assertEqual(len(body["steps"]), 3)

    def test_solves_system_of_equations(self) -> None:
        response = self.client.post(
            "/v1/equation/solve",
            json={"equation": "x+y=5\nx-y=1", "showSteps": False},
        )

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["result"], "x = 3, y = 2")
        self.assertEqual(body["steps"], [])

    def test_rejects_empty_equation(self) -> None:
        response = self.client.post(
            "/v1/equation/solve",
            json={"equation": "   ", "showSteps": True},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "A equação não pode ser vazia")

    def test_rejects_unsupported_equation_type(self) -> None:
        with patch("api.v1.routers.equations.detect_equation_type") as detect_mock:
            detect_mock.return_value = object()

            response = self.client.post(
                "/v1/equation/solve",
                json={"equation": "2+2=4", "showSteps": True},
            )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json()["detail"],
            "Tipo de equação não suportada para resolução",
        )

    def test_solves_inequality(self) -> None:
        response = self.client.post(
            "/v1/equation/solve",
            json={"equation": "2x + 3 > 11", "showSteps": False},
        )

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["result"], "x > 4")
        self.assertEqual(body["steps"], [])

    def test_solves_simplification(self) -> None:
        response = self.client.post(
            "/v1/equation/solve",
            json={"equation": "2x + 3x + 5", "showSteps": False},
        )

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["result"], "5x+5")
        self.assertEqual(body["steps"], [])

    def test_solves_function_analysis_domain(self) -> None:
        response = self.client.post(
            "/v1/equation/solve",
            json={"equation": "domain: 1/(x-2)", "showSteps": False},
        )

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertIn("Domínio:", body["result"])
        self.assertEqual(body["steps"], [])


if __name__ == "__main__":
    unittest.main()
