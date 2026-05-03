from abc import ABC
from abc import abstractmethod

from domain.conversation.models.explanation_model import ExplanationModel


class AiAdapterAbstraction(ABC):
    @abstractmethod
    def retrieve_explanation(self, topic: str) -> ExplanationModel:
        raise NotImplementedError()


AiClient = AiAdapterAbstraction