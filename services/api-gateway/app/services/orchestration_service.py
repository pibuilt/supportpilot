import os
import httpx


class OrchestrationService:
    AI_SERVICE_URL = os.getenv(
        "AI_SERVICE_URL",
        "http://ai-service:8000/v1/orchestrate",
    )

    def process(
        self,
        document_id: str | None,
        query: str,
        session_id: str | None = None,
        context_limit: int = 5,
    ):
        payload = {
            "query": query,
            "context_limit": context_limit,
        }

        if document_id:
            payload["document_id"] = document_id

        if session_id:
            payload["session_id"] = session_id

        response = httpx.post(
            self.AI_SERVICE_URL,
            json=payload,
            timeout=120.0,
        )

        response.raise_for_status()

        return response.json()