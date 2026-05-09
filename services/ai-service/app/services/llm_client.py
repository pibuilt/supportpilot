import httpx


class LLMClient:
    BASE_URL = "http://llm-service:8001"

    async def generate(self, prompt: str):
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/v1/generate",
                json={
                    "prompt": prompt,
                    "max_tokens": 1000,
                    "temperature": 0.2,
                },
            )

            response.raise_for_status()

            return response.json()