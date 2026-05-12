from abc import ABC
from abc import abstractmethod

class CacheServiceAbstraction(ABC):
    @abstractmethod
    def read_json_entry(self, namespace: str, key: str) -> str | None:
        raise NotImplementedError()

    @abstractmethod
    def write_json_entry(self, namespace: str, key: str, value: str, ttl_seconds: int | None = None) -> None:
        raise NotImplementedError()