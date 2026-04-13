import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

APP_DIR = (
    Path(__file__).parent.parent.parent
    / "src"
    / "equation-solver-mobile-bff"
    / "presentation.application"
)
sys.path.insert(0, str(APP_DIR))

from main import app  # noqa: E402
from api.v1.dependencies.auth import AuthenticatedUser, get_current_user  # noqa: E402
from api.v1.conversation.repositories.conversation_repository import (  # noqa: E402
    get_past_conversations_dep,
    get_recent_conversation_dep,
)
from api.v1.conversation.schemas.conversation import (  # noqa: E402
    Conversation,
    ConversationMessage,
)


@pytest.fixture
def client():
    app.dependency_overrides.clear()
    return TestClient(app)


MOCK_USER = AuthenticatedUser(user_id="user-123", token="test-token")

MOCK_CONVERSATION = Conversation(
    id="conv-abc",
    user_id="user-123",
    messages=[
        ConversationMessage(role="user", content="What is an equation?"),
        ConversationMessage(role="assistant", content="An equation is..."),
    ],
    started_at="2026-04-13T10:00:00Z",
)

MOCK_PAST_CONVERSATIONS = [
    Conversation(
        id="conv-old",
        user_id="user-123",
        messages=[
            ConversationMessage(role="user", content="First question"),
            ConversationMessage(role="assistant", content="First answer"),
        ],
        started_at="2026-04-11T10:00:00Z",
    ),
    Conversation(
        id="conv-mid",
        user_id="user-123",
        messages=[
            ConversationMessage(role="user", content="Second question"),
            ConversationMessage(role="assistant", content="Second answer"),
        ],
        started_at="2026-04-12T10:00:00Z",
    ),
    Conversation(
        id="conv-new",
        user_id="user-123",
        messages=[
            ConversationMessage(role="user", content="Third question"),
            ConversationMessage(role="assistant", content="Third answer"),
        ],
        started_at="2026-04-13T10:00:00Z",
    ),
]


@pytest.fixture
def mock_no_recent_conversation(client):
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    app.dependency_overrides[get_recent_conversation_dep] = lambda: None
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_with_recent_conversation(client):
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    app.dependency_overrides[get_recent_conversation_dep] = lambda: MOCK_CONVERSATION
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_no_past_conversations(client):
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    app.dependency_overrides[get_past_conversations_dep] = lambda: []
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_with_past_conversations(client):
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    app.dependency_overrides[get_past_conversations_dep] = lambda: MOCK_PAST_CONVERSATIONS
    yield
    app.dependency_overrides.clear()
