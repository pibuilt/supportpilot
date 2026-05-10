import json
import os

import httpx
from app.providers.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
        self.default_model = os.getenv("OLLAMA_LLM_MODEL", "mistral")
        self.embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

    async def generate(self, prompt: str, model: str | None = None) -> str:
        payload = {
            "model": model or self.default_model,
            "prompt": prompt,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )

            response.raise_for_status()
            data = response.json()

            return data.get("response", "")

    async def stream_generate(
        self,
        prompt: str,
        model: str | None = None,
    ):
        payload = {
            "model": model or self.default_model,
            "prompt": prompt,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload,
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line:
                        continue

                    data = json.loads(line)

                    token = data.get("response", "")

                    if token:
                        yield token

    async def embed(self, text: str) -> list[float]:
        payload = {
            "model": self.embedding_model,
            "prompt": text,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/embeddings",
                json=payload,
            )

            response.raise_for_status()
            data = response.json()

            return data.get("embedding", [])