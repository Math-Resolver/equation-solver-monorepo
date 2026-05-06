from dataclasses import dataclass


@dataclass(frozen=True)
class GeminiRequestModel:
    contents: list["GeminiRequestContentModel"]
    generation_config: "GeminiRequestGenerationConfigModel"

    @classmethod
    def from_prompt(cls, prompt: str, response_mime_type: str = "application/json") -> "GeminiRequestModel":
        return cls(
            contents=[
                GeminiRequestContentModel(
                    parts=[GeminiRequestPartModel(text=prompt)]
                )
            ],
            generation_config=GeminiRequestGenerationConfigModel(
                response_mime_type=response_mime_type,
            )
        )

    def to_dict(self) -> dict:
        return {
            "contents": [content.to_dict() for content in self.contents],
            "generationConfig": self.generation_config.to_dict()
        }


@dataclass(frozen=True)
class GeminiRequestContentModel:
    parts: list["GeminiRequestPartModel"]

    def to_dict(self) -> dict:
        return {"parts": [part.to_dict() for part in self.parts]}


@dataclass(frozen=True)
class GeminiRequestPartModel:
    text: str

    def to_dict(self) -> dict:
        return {"text": self.text}


@dataclass(frozen=True)
class GeminiRequestGenerationConfigModel:
    response_mime_type: str

    def to_dict(self) -> dict:
        return {"responseMimeType": self.response_mime_type}