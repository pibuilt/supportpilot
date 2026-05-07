from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):

    @abstractmethod
    async def generate(self, prompt: str, model: str | None = None) -> str:
        pass

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        pass