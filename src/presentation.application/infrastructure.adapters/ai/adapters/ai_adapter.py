import logging
import json
import os
from pathlib import Path
from urllib import request
from urllib.error import HTTPError
from domain.module_loader import load_module_from_path
from domain.abstractions.ai_adapter_abstraction import AiAdapterAbstraction
from domain.conversation.models.explanation_model import ExplanationModel


_MODEL_MODULE = load_module_from_path(
    "infrastructure.adapters.ai.models.gemini_response_model",
    Path(__file__).resolve().parents[1] / "models" / "gemini_response_model.py",
)

GeminiResponseModel = _MODEL_MODULE.GeminiResponseModel


_REQUEST_MODEL_MODULE = load_module_from_path(
    "infrastructure.adapters.ai.models.gemini_request_model",
    Path(__file__).resolve().parents[1] / "models" / "gemini_request_model.py",
)

GeminiRequestModel = _REQUEST_MODEL_MODULE.GeminiRequestModel

logger = logging.getLogger(__name__)

AI_MODEL = "gemini-2.0-flash"
DEFAULT_TIMEOUT_SECONDS = 10


class AiAdapter(AiAdapterAbstraction):
    def __init__(self, api_key: str, model: str, timeout_seconds: int):
        self._api_key = api_key
        self._model = model
        self._timeout_seconds = timeout_seconds

    def retrieve_explanation(self, topic: str) -> ExplanationModel:
        prompt = _build_prompt(topic)
        gemini_request = GeminiRequestModel.from_prompt(prompt).to_dict()
        endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._model}:generateContent?key={self._api_key}"
        )
        http_request = _build_http_request(endpoint, gemini_request)
        try:
            with request.urlopen(http_request, timeout=self._timeout_seconds) as response:
                response_body = response.read().decode("utf-8")
        except HTTPError as exc:
            if exc.code == 429:
                logger.warning("Gemini rate limit exceeded (HTTP 429).")
                return ExplanationModel(is_operation_successful=False, message="Ai model is unavailable for now")
        try:
            gemini_response = GeminiResponseModel.from_json(response_body)
            parsed_text = gemini_response.first_payload()
        except Exception as exc:
            logger.error("Failed to deserialize Gemini response. response_body=%s", response_body, exc_info=exc)
            return ExplanationModel(is_operation_successful=False, message="Failed to deserialize response")
        message = parsed_text.message
        example = parsed_text.example
        return ExplanationModel(is_operation_successful=True, message=message.strip(), example=example)
    

def get_ai_adapter() -> AiAdapter:
    api_key = os.getenv("AI_API_KEY")
    model = os.getenv("AI_MODEL", AI_MODEL)
    timeout_seconds = int(
        os.getenv("TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
    )
    return AiAdapter(api_key=api_key, model=model, timeout_seconds=timeout_seconds)


GeminiClient = AiAdapter
get_gemini_client = get_ai_adapter


def _build_prompt(topic: str) -> str:
    prompt = (
        "You are a math tutor. Explain the requested topic in a concise educational way. "
        "Return valid JSON with keys 'message' and 'example'. The 'message' must be a short "
        "explanation for a student and 'example' must be either a short math example. "
        f"Topic: {topic}"
    )
    return prompt


def _build_http_request(endpoint: str, gemini_request: GeminiRequestModel) -> request.Request:
    http_request = request.Request(
        endpoint,
        data=json.dumps(gemini_request).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    return http_request