import httpx

from langchain_core.tools import (
    StructuredTool,
)
from pydantic import BaseModel


class RetrievalInput(
    BaseModel
):
    owner_id: str
    tenant_id: str
    api_key: str

    query: str
    document_id: str | None = None

    top_k: int = 5


async def retrieval_function(
    owner_id: str,
    tenant_id: str,
    api_key: str,

    query: str,
    document_id: str | None = None,
    top_k: int = 5,
):
    payload = {
        "query": query,
        "top_k": top_k,
    }

    if document_id:
        payload[
            "document_id"
        ] = document_id

    headers = {
        "x-api-key": api_key,
    }

    async with httpx.AsyncClient(
        timeout=60.0
    ) as client:
        response = await client.post(
            "http://api-gateway:8000/v1/search",
            json=payload,
            headers=headers,
        )

        response.raise_for_status()

        result = response.json()

        return {
            "tool": "retrieval",

            "owner_id": owner_id,
            "tenant_id": tenant_id,

            "query": query,
            "document_id": document_id,

            "results": result[
                "data"
            ][
                "results"
            ],

            "summary": result[
                "data"
            ][
                "summary"
            ],

            "status": "success",
        }


retrieval_tool = (
    StructuredTool.from_function(
        coroutine=retrieval_function,
        name="retrieval",
        description=(
            "Retrieve relevant legal clauses "
            "or evidence from indexed "
            "documents."
        ),
        args_schema=RetrievalInput,
    )
)