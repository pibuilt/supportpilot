from fastapi import APIRouter, Request
import time
from app.schemas.health import HealthResponse
from app.utils.response import success_response

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(request: Request):
    request_id = request.state.request_id

    data = HealthResponse(
        status="ok",
        timestamp=time.time()
    )

    return success_response(
        data=data.model_dump(),
        request_id=request_id
    )