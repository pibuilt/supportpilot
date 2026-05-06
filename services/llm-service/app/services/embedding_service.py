from app.services.llm_factory import get_provider


async def generate_embedding(
    text: str,
    provider: str,
    model: str
) -> list[float]:

    llm_provider = get_provider(provider)

    return await llm_provider.embed(
        text=text,
        model=model
    )