"""
🔴 RED → 🟢 GREEN → 🔵 REFACTOR

Unit tests for GET /conversation/history endpoint.

Expected behaviors:
  1. Not authenticated                     → 401
  2. Authenticated, no conversation in 12h → 200 | has_recent_conversation=False | status=NO_CONVERSATION_STARTED
  3. Authenticated, conversation in 12h    → 200 | has_recent_conversation=True  | full conversation
"""


class TestConversationHistory:
    def test_should_return_401_when_user_is_not_authenticated(self, client):
        response = client.get("/conversation/history")

        assert response.status_code == 401

    def test_should_return_200_and_no_conversation_status_when_no_conversation_in_last_12_hours(
        self, client, mock_no_recent_conversation):
        response = client.get("/conversation/history")

        assert response.status_code == 200
        body = response.json()
        assert body["has_recent_conversation"] is False
        assert body["status"] == "NO_CONVERSATION_STARTED"
        assert body["conversation"] is None

    def test_should_return_200_with_full_conversation_when_conversation_exists_in_last_12_hours(
        self, client, mock_with_recent_conversation):
        response = client.get("/conversation/history")

        assert response.status_code == 200
        body = response.json()
        assert body["has_recent_conversation"] is True
        assert body["status"] is None
        assert body["conversation"] is not None
        assert body["conversation"]["id"] == "conv-abc"
        assert body["conversation"]["user_id"] == "user-123"
        assert len(body["conversation"]["messages"]) == 2
        assert body["conversation"]["messages"][0]["role"] == "user"
        assert body["conversation"]["messages"][0]["content"] == "What is an equation?"
        assert body["conversation"]["messages"][1]["role"] == "assistant"