import os
import httpx


class OrchestrationService:
    AI_SERVICE_URL = os.getenv(
        "AI_SERVICE_URL",
        "http://ai-service:8000/v1/orchestrate",
    )

    def process(
        self,
        owner_id: str,
        tenant_id: str,
        api_key: str,

        document_id: str | None,
        query: str,

        session_id: str | None = None,
        context_limit: int = 5,
    ):
        payload = {
            "owner_id": owner_id,
            "tenant_id": tenant_id,
            "api_key": api_key,

            "query": query,
            "context_limit": context_limit,
        }

        if document_id:
            payload[
                "document_id"
            ] = document_id

        if session_id:
            payload[
                "session_id"
            ] = session_id

        response = httpx.post(
            self.AI_SERVICE_URL,
            json=payload,
            timeout=120.0,
        )

        response.raise_for_status()

        return response.json()