from enum import Enum

from pydantic import (
    BaseModel,
    EmailStr,
)


class UserRole(
    str,
    Enum,
):
    USER = "user"
    ADMIN = "admin"
    ROOT_ADMIN = "root_admin"


class UserSignupRequest(
    BaseModel
):
    email: EmailStr
    password: str
    full_name: str
    tenant_id: str


class UserLoginRequest(
    BaseModel
):
    email: EmailStr
    password: str


class AuthTokenResponse(
    BaseModel
):
    access_token: str
    token_type: str = (
        "bearer"
    )

    api_key: str
    key_prefix: str

    user_id: str
    email: str
    full_name: str

    role: UserRole
    tenant_id: str


class CurrentUserResponse(
    BaseModel
):
    user_id: str
    email: str
    full_name: str

    role: UserRole
    tenant_id: str

    is_active: bool