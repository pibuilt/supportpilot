import os
import requests


class OllamaClient:
    def __init__(self):
        self.base_url = f"{os.getenv('OLLAMA_URL')}/api/generate"
        self.model = os.getenv("OLLAMA_LLM_MODEL", "mistral")

    def generate(self, prompt: str) -> str:
        response = requests.post(
            self.base_url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )

        response.raise_for_status()
        return response.json()["response"]