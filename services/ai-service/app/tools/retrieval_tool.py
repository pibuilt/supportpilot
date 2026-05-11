from app.tools.base import BaseTool


class RetrievalTool(BaseTool):
    name = "retrieval"
    description = "Retrieve relevant legal clauses or evidence from indexed documents"

    async def execute(
        self,
        query: str,
        document_id: str | None = None,
    ):
        # Placeholder until API Gateway retrieval integration
        return {
            "query": query,
            "document_id": document_id,
            "results": [],
            "status": "retrieval_not_yet_integrated",
        }