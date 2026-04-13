"""
🔴 RED → 🟢 GREEN → 🔵 REFACTOR

Unit tests for GET /conversation/history endpoint.

Expected behaviors:
    1. Not authenticated        → 401
    2. No past conversations    → 200 | empty list
    3. Multiple conversations   → 200 | top 2 most recent by default
    4. Page 2 requested         → 200 | correct slice
"""


class TestConversationHistory:
    def test_should_return_401_when_user_is_not_authenticated(self, client):
        response = client.get("/conversation/history")

        assert response.status_code == 401

    def test_should_return_200_with_empty_payload_when_no_past_conversation_exists(
        self, client, mock_no_past_conversations
    ):
        response = client.get("/conversation/history")

        assert response.status_code == 200
        body = response.json()
        assert body["conversations"] == []
        assert body["page"] == 1
        assert body["limit"] == 2
        assert body["total"] == 0

    def test_should_return_200_with_two_most_recent_conversations_by_default(
        self, client, mock_with_past_conversations
    ):
        response = client.get("/conversation/history")

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 3
        assert body["page"] == 1
        assert body["limit"] == 2
        assert len(body["conversations"]) == 2
        assert body["conversations"][0]["id"] == "conv-new"
        assert body["conversations"][1]["id"] == "conv-mid"

    def test_should_return_second_page_when_query_params_are_provided(
        self, client, mock_with_past_conversations
    ):
        response = client.get("/conversation/history?page=2&limit=2")

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 3
        assert body["page"] == 2
        assert body["limit"] == 2
        assert len(body["conversations"]) == 1
        assert body["conversations"][0]["id"] == "conv-old"

