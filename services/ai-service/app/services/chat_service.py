import json
import time
import uuid

from app.graph.checkpoint import GraphCheckpointService
from app.schemas.chat import (
    ChatCompletionChoice,
    ChatCompletionChoiceMessage,
    ChatCompletionResponse,
    ChatCompletionUsage,
)
from app.services.llm_client import LLMClient
from app.services.memory_service import MemoryService


class ChatService:
    def __init__(self):
        self.llm_client = LLMClient()
        self.memory_service = MemoryService()
        self.checkpoint_service = GraphCheckpointService()

    async def process(
        self,
        model: str,
        messages: list,
        temperature: float,
        max_tokens: int,
        session_id: str | None = None,
    ) -> ChatCompletionResponse:
        session_id = session_id or str(uuid.uuid4())

        conversation_history = self.memory_service.load_session(
            session_id
        )

        prompt = ""

        for msg in conversation_history:
            prompt += (
                f"{msg['role'].upper()}: "
                f"{msg['content']}\n"
            )

        for message in messages:
            role = message.role.upper()
            prompt += f"{role}: {message.content}\n"

        result = await self.llm_client.generate(
            prompt=prompt,
        )

        output_text = result["output"]

        self.memory_service.append_message(
            session_id,
            "user",
            messages[-1].content,
        )

        self.memory_service.append_message(
            session_id,
            "assistant",
            output_text,
        )

        self.checkpoint_service.save_checkpoint(
            session_id,
            {
                "session_id": session_id,
                "conversation_history": self.memory_service.load_session(
                    session_id
                ),
                "final_response": output_text,
            },
        )

        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4()}",
            created=int(time.time()),
            model=model,
            session_id=session_id,
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

    async def stream_process(
        self,
        model: str,
        messages: list,
        temperature: float,
        max_tokens: int,
        session_id: str | None = None,
    ):
        session_id = session_id or str(uuid.uuid4())

        conversation_history = self.memory_service.load_session(
            session_id
        )

        prompt = ""

        for msg in conversation_history:
            prompt += (
                f"{msg['role'].upper()}: "
                f"{msg['content']}\n"
            )

        for message in messages:
            role = message.role.upper()
            prompt += f"{role}: {message.content}\n"

        stream_id = f"chatcmpl-{uuid.uuid4()}"
        full_response = ""

        try:
            async for token in self.llm_client.stream_generate(
                prompt=prompt,
            ):
                if not token.strip():
                    continue

                full_response += token

                chunk = {
                    "id": stream_id,
                    "object": "chat.completion.chunk",
                    "session_id": session_id,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "content": token
                            },
                            "finish_reason": None,
                        }
                    ],
                }

                yield (
                    f"data: {json.dumps(chunk)}\n\n"
                )

            self.memory_service.append_message(
                session_id,
                "user",
                messages[-1].content,
            )

            self.memory_service.append_message(
                session_id,
                "assistant",
                full_response,
            )

            self.checkpoint_service.save_checkpoint(
                session_id,
                {
                    "session_id": session_id,
                    "conversation_history": self.memory_service.load_session(
                        session_id
                    ),
                    "final_response": full_response,
                },
            )

            yield "data: [DONE]\n\n"

        except Exception as e:
            error_chunk = {
                "id": stream_id,
                "object": "chat.completion.chunk",
                "session_id": session_id,
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "content": ""
                        },
                        "finish_reason": "error",
                    }
                ],
                "error": str(e),
            }

            yield (
                f"data: {json.dumps(error_chunk)}\n\n"
            )

            yield "data: [DONE]\n\n"