from pydantic import BaseModel
from typing import Any, Optional


class SuccessResponse(BaseModel):
    data: Any
    request_id: str


class ErrorDetail(BaseModel):
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorDetail