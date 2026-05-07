import os
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_provider import OpenAIProvider


def get_llm_provider(provider_name: str | None = None):
    provider = provider_name or os.getenv("LLM_PROVIDER", "ollama")

    if provider.lower() == "openai":
        return OpenAIProvider()

    return OllamaProvider()