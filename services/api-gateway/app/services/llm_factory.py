import os

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI


def get_llm():
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "ollama":
        return ChatOllama(
            base_url=os.getenv("OLLAMA_URL"),
            model=os.getenv("OLLAMA_LLM_MODEL"),
            temperature=0,
            validate_model_on_init=True,
        )

    elif provider == "openai":
        return ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            model=os.getenv("OPENAI_MODEL"),
            temperature=0,
        )

    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}"
        )