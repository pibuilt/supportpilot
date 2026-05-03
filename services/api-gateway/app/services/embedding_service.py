import os
import requests


OLLAMA_URL = os.getenv(
    "OLLAMA_URL"
)

OLLAMA_EMBEDDING_MODEL = os.getenv(
    "OLLAMA_EMBEDDING_MODEL"
)


def generate_embedding(text: str) -> list[float]:
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={
            "model": OLLAMA_EMBEDDING_MODEL,
            "prompt": text,
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()["embedding"]