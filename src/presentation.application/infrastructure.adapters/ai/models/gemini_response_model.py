import json
from dataclasses import dataclass


@dataclass(frozen=True)
class GeminiResponseModel:
    candidates: list["GeminiResponseCandidateModel"]

    @classmethod
    def from_json(cls, response_body: str) -> "GeminiResponseModel":
        payload = json.loads(response_body)
        return cls(
            candidates=[
                GeminiResponseCandidateModel(
                    content=GeminiResponseContentModel(
                        parts=[
                            GeminiResponsePartModel(text=part_payload["text"])
                            for part_payload in candidate_payload["content"]["parts"]
                        ]
                    )
                )
                for candidate_payload in payload["candidates"]
            ]
        )

    def first_text(self) -> str:
        return self.candidates[0].content.parts[0].text

    def first_payload(self) -> "GeminiGeneratedPayloadModel":
        return self.candidates[0].content.parts[0].payload()


@dataclass(frozen=True)
class GeminiGeneratedPayloadModel:
    message: str
    example: str | None = None

    @classmethod
    def from_text(cls, text: str) -> "GeminiGeneratedPayloadModel":
        payload = json.loads(text)
        return cls(message=payload.get("message"), example=payload.get("example"))


@dataclass(frozen=True)
class GeminiResponseCandidateModel:
    content: "GeminiResponseContentModel"


@dataclass(frozen=True)
class GeminiResponseContentModel:
    parts: list["GeminiResponsePartModel"]


@dataclass(frozen=True)
class GeminiResponsePartModel:
    text: str

    def payload(self) -> "GeminiGeneratedPayloadModel":
        return GeminiGeneratedPayloadModel.from_text(self.text)