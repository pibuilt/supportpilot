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
    user_id: Optional[str] = None
    role: Optional[str] = None
    tenant_id: Optional[str] = None
    api_key_id: Optional[str] = None


class APIKeySummaryResponse(BaseModel):
    api_key_id: str
    key_prefix: str
    owner: str
    role: str
    tenant_id: str
    is_active: bool
    created_at: Any


class APIKeyIssueResponse(BaseModel):
    api_key_id: str
    api_key: str
    key_prefix: str
