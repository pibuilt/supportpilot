from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float = 0.2
    ) -> str:
        pass

    @abstractmethod
    async def embed(
        self,
        text: str,
        model: str
    ) -> list[float]:
        pass