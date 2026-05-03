import json

from main import app
from api.v1.dependencies.service_injection import get_ai_adapter
from api.v1.dependencies.service_injection import get_cache_service
from domain.conversation.constants.topics import Topics
from domain.conversation.models.explanation_model import ExplanationModel


class CacheUnavailableError(Exception):
    pass


class TestAvailableTopics:
    def test_should_return_401_when_user_is_not_authenticated(self, client):
        response = client.get("/v1/topics/available")

        assert response.status_code == 401

    def test_should_return_available_topics_when_user_is_authenticated(
        self, client, mock_authenticated_user
    ):
        response = client.get("/v1/topics/available")

        assert response.status_code == 200
        assert response.json() == {"topics": Topics.list()}


class TestCreateConversation:
    def test_should_return_401_when_user_is_not_authenticated(self, client):
        response = client.post("/v1/conversation", json={"topic": "Logarithm"})

        assert response.status_code == 401

    def test_should_return_cached_response_without_calling_ai_when_cache_hit(
        self, client, mock_authenticated_user
    ):
        cache_service = FakeCacheService(
            cached_response=json.dumps({
                "is_operation_successful": True,
                "message": "A logarithm is the inverse operation of exponentiation.",
                "example": None,
            })
        )
        ai_adapter = FakeAiAdapter()

        app.dependency_overrides[get_cache_service] = lambda: cache_service
        app.dependency_overrides[get_ai_adapter] = lambda: ai_adapter

        response = client.post("/v1/conversation", json={"topic": "Logarithm"})

        assert response.status_code == 200
        assert response.json() == {
            "is_operation_successful": True,
            "message": "A logarithm is the inverse operation of exponentiation.",
        }
        assert cache_service.requested_keys == [("conversation:topic", "Logarithm")]
        assert ai_adapter.requested_topics == []

    def test_should_call_ai_and_store_response_when_cache_misses(
        self, client, mock_authenticated_user
    ):
        cache_service = FakeCacheService()
        ai_adapter = FakeAiAdapter(
            response=ExplanationModel(
                is_operation_successful=True,
                message="A logarithm tells which exponent produces a value.",
                example="log2(8) = 3 because 2^3 = 8.",
            )
        )

        app.dependency_overrides[get_cache_service] = lambda: cache_service
        app.dependency_overrides[get_ai_adapter] = lambda: ai_adapter

        response = client.post("/v1/conversation", json={"topic": "Logarithm"})

        assert response.status_code == 200
        assert response.json() == {
            "is_operation_successful": True,
            "message": "A logarithm tells which exponent produces a value.",
            "example": "log2(8) = 3 because 2^3 = 8.",
        }
        assert ai_adapter.requested_topics == ["Logarithm"]
        assert cache_service.saved_entries == [
            (
                "conversation:topic",
                "Logarithm",
                json.dumps({
                    "is_operation_successful": True,
                    "message": "A logarithm tells which exponent produces a value.",
                    "example": "log2(8) = 3 because 2^3 = 8.",
                }),
                None,
            )
        ]

    def test_should_fallback_to_ai_when_redis_is_unavailable(
        self, client, mock_authenticated_user
    ):
        cache_service = FakeCacheService(get_error=CacheUnavailableError("redis down"))
        ai_adapter = FakeAiAdapter(
            response=ExplanationModel(
                is_operation_successful=True,
                message="Logarithms convert multiplication into addition.",
                example="log(ab) = log(a) + log(b).",
            )
        )

        app.dependency_overrides[get_cache_service] = lambda: cache_service
        app.dependency_overrides[get_ai_adapter] = lambda: ai_adapter

        response = client.post("/v1/conversation", json={"topic": "Logarithm"})

        assert response.status_code == 200
        assert response.json() == {
            "is_operation_successful": True,
            "message": "Logarithms convert multiplication into addition.",
            "example": "log(ab) = log(a) + log(b).",
        }
        assert ai_adapter.requested_topics == ["Logarithm"]

    def test_should_return_http_error_when_ai_fails(
        self, client, mock_authenticated_user
    ):
        cache_service = FakeCacheService()
        ai_adapter = FakeAiAdapter(
            response=ExplanationModel(
                is_operation_successful=False,
                message="Gemini request failed",
            )
        )

        app.dependency_overrides[get_cache_service] = lambda: cache_service
        app.dependency_overrides[get_ai_adapter] = lambda: ai_adapter

        response = client.post("/v1/conversation", json={"topic": "Logarithm"})

        assert response.status_code == 502
        assert response.json() == {
            "is_operation_successful": False,
            "message": "Gemini request failed",
        }

class FakeCacheService:
    def __init__(self, cached_response=None, get_error=None, set_error=None):
        self.cached_response = cached_response
        self.get_error = get_error
        self.set_error = set_error
        self.requested_keys = []
        self.saved_entries = []

    def read_json_entry(self, namespace, key):
        self.requested_keys.append((namespace, key))

        if self.get_error is not None:
            raise self.get_error

        return self.cached_response

    def write_json_entry(self, namespace, key, response, ttl_seconds=None):
        if self.set_error is not None:
            raise self.set_error

        self.saved_entries.append((namespace, key, response, ttl_seconds))


class FakeAiAdapter:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.requested_topics = []

    def retrieve_explanation(self, topic):
        self.requested_topics.append(topic)

        if self.error is not None:
            raise self.error

        return self.response