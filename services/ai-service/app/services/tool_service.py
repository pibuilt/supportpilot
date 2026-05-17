from app.tools.registry import ToolRegistry


class ToolService:
    def __init__(self):
        self.registry = ToolRegistry()

    async def execute_tool(
        self,
        tool_name: str,
        **kwargs,
    ):
        tool = self.registry.get_tool(
            tool_name
        )

        if not tool:
            return {
                "error": (
                    f"Tool '{tool_name}' not found"
                )
            }

        # Hard security validation
        owner_id = kwargs.get(
            "owner_id"
        )

        tenant_id = kwargs.get(
            "tenant_id"
        )

        if not owner_id or not tenant_id:
            return {
                "error": (
                    "Missing owner_id or tenant_id "
                    "for secure tool execution"
                )
            }

        # Ensure all tools inherit ownership context
        secure_payload = dict(
            kwargs
        )

        secure_payload[
            "owner_id"
        ] = owner_id

        secure_payload[
            "tenant_id"
        ] = tenant_id

        return await tool.ainvoke(
            secure_payload
        )

    def list_tools(
        self,
    ):
        return (
            self.registry.list_tools()
        )

    def get_all_tools(
        self,
    ):
        return (
            self.registry.get_all_tools()
        )