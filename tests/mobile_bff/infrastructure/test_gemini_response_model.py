import json

import pytest

from infrastructure.adapters.ai.models.gemini_request_model import GeminiRequestModel
from infrastructure.adapters.ai.models.gemini_response_model import GeminiGeneratedPayloadModel
from infrastructure.adapters.ai.models.gemini_response_model import GeminiResponsePartModel
from infrastructure.adapters.ai.models.gemini_response_model import GeminiResponseModel


class TestGeminiRequestModel:
    def test_should_build_request_payload_from_prompt(self):
        request_model = GeminiRequestModel.from_prompt("Explain logarithms")

        assert request_model.to_dict() == {
            "contents": [{"parts": [{"text": "Explain logarithms"}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        }


class TestGeminiResponseModel:
    def test_should_return_first_payload_as_model(self):
        response_body = json.dumps({
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps({
                                    "message": "A logarithm is the inverse of exponentiation.",
                                    "example": "log2(8) = 3",
                                })
                            }
                        ]
                    }
                }
            ]
        })

        response_model = GeminiResponseModel.from_json(response_body)

        assert response_model.first_payload() == GeminiGeneratedPayloadModel(
            message="A logarithm is the inverse of exponentiation.",
            example="log2(8) = 3",
        )

    def test_should_raise_type_error_when_first_payload_is_not_a_json_object(self):
        response_body = json.dumps({
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps(["invalid", "payload"])
                            }
                        ]
                    }
                }
            ]
        })

        response_model = GeminiResponseModel.from_json(response_body)

        with pytest.raises(TypeError):
            response_model.first_payload()


class TestGeminiResponsePartModel:
    def test_should_parse_payload_from_text(self):
        part_model = GeminiResponsePartModel(
            text=json.dumps({
                "message": "A logarithm is the inverse of exponentiation.",
                "example": "log2(8) = 3",
            })
        )

        assert part_model.payload() == GeminiGeneratedPayloadModel(
            message="A logarithm is the inverse of exponentiation.",
            example="log2(8) = 3",
        )

    def test_should_fallback_to_plain_text_message(self):
        part_model = GeminiResponsePartModel(
            text="A logarithm is the inverse of exponentiation."
        )

        assert part_model.payload() == GeminiGeneratedPayloadModel(
            message="A logarithm is the inverse of exponentiation.",
            example=None,
        )