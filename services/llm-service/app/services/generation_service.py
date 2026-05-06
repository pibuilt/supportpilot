from app.services.llm_factory import get_provider


async def generate_text(
    system_prompt: str,
    user_prompt: str,
    provider: str,
    model: str,
    temperature: float = 0.2
) -> str:

    llm_provider = get_provider(provider)

    return await llm_provider.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=model,
        temperature=temperature
    )