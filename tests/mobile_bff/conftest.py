import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

APP_DIR = (
    Path(__file__).parent.parent.parent
    / "src"
    / "presentation.application"
)
sys.path.insert(0, str(APP_DIR))

from main import app  # noqa: E402
from api.v1.dependencies.auth import AuthenticatedUser, get_current_user  # noqa: E402


@pytest.fixture
def client():
    app.dependency_overrides.clear()
    return TestClient(app)


MOCK_USER = AuthenticatedUser(user_id="user-123", token="test-token")

@pytest.fixture
def mock_authenticated_user(client):
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    yield MOCK_USER
    app.dependency_overrides.clear()
