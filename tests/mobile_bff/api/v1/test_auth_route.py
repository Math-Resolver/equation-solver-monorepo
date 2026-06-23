import unittest
import sys
from pathlib import Path

from fastapi.testclient import TestClient

APP_DIR = (
    Path(__file__).resolve().parents[4]
    / "src"
    / "presentation.application"
)
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from main import app
from api.v1.auth.routers.auth import reset_auth_state_for_tests


class AuthRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_auth_state_for_tests()
        self.client = TestClient(app)

    def test_register_is_idempotent_for_same_device(self) -> None:
        payload = {
            "displayName": "user@email.com",
            "deviceFingerprint": "iphone15-uuid",
        }

        response_a = self.client.post("/v1/auth/register", json=payload)
        response_b = self.client.post("/v1/auth/register", json=payload)

        self.assertEqual(response_a.status_code, 200)
        self.assertEqual(response_b.status_code, 200)
        self.assertEqual(response_a.json()["challenge"], response_b.json()["challenge"])

    def test_register_returns_conflict_for_existing_registered_user(self) -> None:
        self.client.post(
            "/v1/auth/register",
            json={"displayName": "user@email.com", "deviceFingerprint": "iphone15-uuid"},
        )
        self.client.post(
            "/v1/auth/register/finish",
            json={"email": "user@email.com", "credential": "valid-credential"},
        )

        response = self.client.post(
            "/v1/auth/register",
            json={"displayName": "user@email.com", "deviceFingerprint": "iphone15-uuid"},
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["detail"], "displayName já cadastrado")

    def test_register_finish_returns_401_for_invalid_credential(self) -> None:
        self.client.post(
            "/v1/auth/register",
            json={"displayName": "user@email.com", "deviceFingerprint": "iphone15-uuid"},
        )

        response = self.client.post(
            "/v1/auth/register/finish",
            json={"email": "user@email.com", "credential": "invalid-credential"},
        )

        self.assertEqual(response.status_code, 401)

    def test_login_finish_returns_access_and_refresh_tokens(self) -> None:
        self.client.post(
            "/v1/auth/register",
            json={"displayName": "user@email.com", "deviceFingerprint": "iphone15-uuid"},
        )
        self.client.post(
            "/v1/auth/register/finish",
            json={"email": "user@email.com", "credential": "valid-credential"},
        )
        self.client.post("/v1/auth/login", json={"email": "user@email.com"})

        response = self.client.post(
            "/v1/auth/login/finish",
            json={"email": "user@email.com", "credential": "valid-credential"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("access_token", body)
        self.assertIn("refresh_token", body)

    def test_refresh_token_rotates_and_revokes_previous_token(self) -> None:
        self.client.post(
            "/v1/auth/register",
            json={"displayName": "user@email.com", "deviceFingerprint": "iphone15-uuid"},
        )
        self.client.post(
            "/v1/auth/register/finish",
            json={"email": "user@email.com", "credential": "valid-credential"},
        )
        self.client.post("/v1/auth/login", json={"email": "user@email.com"})
        login_finish = self.client.post(
            "/v1/auth/login/finish",
            json={"email": "user@email.com", "credential": "valid-credential"},
        )
        first_refresh_token = login_finish.json()["refresh_token"]

        refresh_response = self.client.post(
            "/v1/auth/refresh-token",
            json={"token": first_refresh_token},
        )

        self.assertEqual(refresh_response.status_code, 200)
        second_refresh_token = refresh_response.json()["refresh_token"]
        self.assertNotEqual(first_refresh_token, second_refresh_token)

        revoked_response = self.client.post(
            "/v1/auth/refresh-token",
            json={"token": first_refresh_token},
        )
        self.assertEqual(revoked_response.status_code, 401)

    def test_protected_endpoints_accept_access_token(self) -> None:
        self.client.post(
            "/v1/auth/register",
            json={"displayName": "user@email.com", "deviceFingerprint": "iphone15-uuid"},
        )
        self.client.post(
            "/v1/auth/register/finish",
            json={"email": "user@email.com", "credential": "valid-credential"},
        )
        self.client.post("/v1/auth/login", json={"email": "user@email.com"})
        login_finish = self.client.post(
            "/v1/auth/login/finish",
            json={"email": "user@email.com", "credential": "valid-credential"},
        )
        access_token = login_finish.json()["access_token"]

        response = self.client.get(
            "/v1/topics/available",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
