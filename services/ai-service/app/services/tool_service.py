from app.tools.registry import ToolRegistry


class ToolService:
    def __init__(self):
        self.registry = ToolRegistry()

    async def execute_tool(
        self,
        tool_name: str,
        **kwargs,
    ):
        tool = self.registry.get_tool(tool_name)

        if not tool:
            return {
                "error": f"Tool '{tool_name}' not found"
            }

        return await tool.ainvoke(kwargs)

    def list_tools(
        self,
    ):
        return self.registry.list_tools()

    def get_all_tools(
        self,
    ):
        return self.registry.get_all_tools()