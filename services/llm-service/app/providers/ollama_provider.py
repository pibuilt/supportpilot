import json
import os
from urllib import response

import httpx
from app.providers.base import BaseLLMProvider
from langsmith import traceable


class OllamaProvider(BaseLLMProvider):
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://172.17.0.1:11434")
        self.default_model = os.getenv("OLLAMA_LLM_MODEL", "qwen2.5:1.5b")
        self.embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text:latest")

    @traceable(name="ollama_generate")
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

            if response.status_code != 200:
                raise Exception(
                    f"Ollama Error {response.status_code}: {response.text}"
                )
            data = response.json()

            return data.get("response", "")

    @traceable(name="ollama_stream_generate")
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
                if response.status_code != 200:
                    raise Exception(
                        f"Ollama Error {response.status_code}: {response.text}"
                    )

                async for line in response.aiter_lines():
                    if not line:
                        continue

                    data = json.loads(line)

                    token = data.get("response", "")

                    if token:
                        yield token

    @traceable(name="ollama_embedding_generation")
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

            if response.status_code != 200:
                raise Exception(
                    f"Ollama Error {response.status_code}: {response.text}"
                )
            data = response.json()

            return data.get("embedding", [])