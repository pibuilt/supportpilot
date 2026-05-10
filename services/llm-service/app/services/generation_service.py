from app.services.llm_factory import get_llm_provider


async def generate_text(
    prompt: str,
    provider: str | None = None,
    model: str | None = None,
) -> str:
    llm_provider = get_llm_provider(provider)

    return await llm_provider.generate(
        prompt=prompt,
        model=model,
    )


async def stream_generate_text(
    prompt: str,
    provider: str | None = None,
    model: str | None = None,
):
    llm_provider = get_llm_provider(provider)

    async for token in llm_provider.stream_generate(
        prompt=prompt,
        model=model,
    ):
        yield token