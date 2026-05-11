from app.tools.clause_tool import ClauseTool
from app.tools.retrieval_tool import RetrievalTool


class ToolRegistry:
    def __init__(self):
        self.tools = {
            "retrieval": RetrievalTool(),
            "clause_analysis": ClauseTool(),
        }

    def get_tool(self, tool_name: str):
        return self.tools.get(tool_name)

    def list_tools(self):
        return list(self.tools.keys())