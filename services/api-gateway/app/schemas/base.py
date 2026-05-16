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

class APIKeyCreateRequest(BaseModel):
    owner: str
    role: str = "user"          # user / admin
    tenant_id: str


class APIKeyResponse(BaseModel):
    api_key: str
    key_prefix: str
    owner: str
    role: str
    tenant_id: str


class APIKeyValidationResponse(BaseModel):
    valid: bool
    owner: Optional[str] = None
    role: Optional[str] = None
    tenant_id: Optional[str] = None