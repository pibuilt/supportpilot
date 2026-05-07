import os
from openai import AsyncOpenAI
from app.providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )

        self.default_model = os.getenv("OPENAI_MODEL", "openrouter/auto")

    async def generate(self, prompt: str, model: str | None = None) -> str:
        response = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        return response.choices[0].message.content

    async def embed(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )

        return response.data[0].embedding