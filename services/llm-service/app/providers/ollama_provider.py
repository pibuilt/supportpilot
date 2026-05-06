import os

import httpx

from app.providers.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):

    def __init__(self):
        self.base_url = os.environ["OLLAMA_URL"]

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float = 0.2
    ) -> str:

        payload = {
            "model": model,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )

        response.raise_for_status()

        data = response.json()

        return data["response"]

    async def embed(
        self,
        text: str,
        model: str
    ) -> list[float]:

        payload = {
            "model": model,
            "prompt": text
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/embeddings",
                json=payload
            )

        response.raise_for_status()

        data = response.json()

        return data["embedding"]