from app.providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float = 0.2
    ) -> str:
        raise NotImplementedError

    async def embed(
        self,
        text: str,
        model: str
    ) -> list[float]:
        raise NotImplementedError