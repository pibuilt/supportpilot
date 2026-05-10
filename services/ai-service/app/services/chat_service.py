import time
import uuid

from app.schemas.chat import (
    ChatCompletionChoice,
    ChatCompletionChoiceMessage,
    ChatCompletionResponse,
    ChatCompletionUsage,
)
from app.services.llm_client import LLMClient


class ChatService:
    def __init__(self):
        self.llm_client = LLMClient()

    async def process(
        self,
        model: str,
        messages: list,
        temperature: float,
        max_tokens: int,
    ) -> ChatCompletionResponse:
        prompt = ""

        for message in messages:
            role = message.role.upper()
            prompt += f"{role}: {message.content}\n"

        result = await self.llm_client.generate(
            prompt=prompt,
        )

        output_text = result["output"]

        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4()}",
            created=int(time.time()),
            model=model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatCompletionChoiceMessage(
                        role="assistant",
                        content=output_text,
                    ),
                    finish_reason="stop",
                )
            ],
            usage=ChatCompletionUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
            ),
        )