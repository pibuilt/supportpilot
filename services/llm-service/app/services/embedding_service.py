from app.services.llm_factory import get_llm_provider


async def generate_embedding(
    text: str,
    provider: str | None = None,
) -> list[float]:
    llm_provider = get_llm_provider(provider)

    return await llm_provider.embed(text=text)