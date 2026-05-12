from app.tools.clause_tool import clause_tool
from app.tools.retrieval_tool import retrieval_tool


class ToolRegistry:
    def __init__(self):
        self.tools = {
            "retrieval": retrieval_tool,
            "clause_analysis": clause_tool,
        }

    def get_tool(
        self,
        tool_name: str,
    ):
        return self.tools.get(tool_name)

    def list_tools(
        self,
    ):
        return list(self.tools.keys())

    def get_all_tools(
        self,
    ):
        return list(self.tools.values())