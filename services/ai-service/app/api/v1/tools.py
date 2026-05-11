from fastapi import APIRouter

from app.services.tool_service import ToolService

router = APIRouter(
    prefix="/v1/tools",
    tags=["tools"],
)

service = ToolService()


@router.get("")
async def list_tools():
    return {
        "tools": service.list_tools(),
    }