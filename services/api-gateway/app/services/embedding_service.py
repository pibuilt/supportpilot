import os
import requests


OLLAMA_URL = os.getenv(
    "OLLAMA_URL"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL"
)


def generate_embedding(text: str) -> list[float]:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": text,
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()["embedding"]