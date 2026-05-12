from langchain_core.tools import StructuredTool
from pydantic import BaseModel


class RetrievalInput(BaseModel):
    query: str
    document_id: str | None = None


async def retrieval_function(
    query: str,
    document_id: str | None = None,
):
    return {
        "tool": "retrieval",
        "query": query,
        "document_id": document_id,
        "results": [],
        "status": "retrieval_not_yet_integrated",
    }


retrieval_tool = StructuredTool.from_function(
    coroutine=retrieval_function,
    name="retrieval",
    description="Retrieve relevant legal clauses or evidence from indexed documents.",
    args_schema=RetrievalInput,
)