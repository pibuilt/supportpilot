import httpx

from langchain_core.tools import StructuredTool
from pydantic import BaseModel


class RetrievalInput(BaseModel):
    query: str
    document_id: str | None = None
    top_k: int = 5


async def retrieval_function(
    query: str,
    document_id: str | None = None,
    top_k: int = 5,
):
    async with httpx.AsyncClient(
        timeout=60.0
    ) as client:
        response = await client.post(
            "http://api-gateway:8000/v1/search",
            json={
                "query": query,
                "document_id": document_id,
                "top_k": top_k,
            },
        )

        response.raise_for_status()

        result = response.json()

        return {
            "tool": "retrieval",
            "query": query,
            "document_id": document_id,
            "results": result["data"]["results"],
            "summary": result["data"]["summary"],
            "status": "success",
        }


retrieval_tool = StructuredTool.from_function(
    coroutine=retrieval_function,
    name="retrieval",
    description="Retrieve relevant legal clauses or evidence from indexed documents.",
    args_schema=RetrievalInput,
)