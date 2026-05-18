import hashlib
import os
import secrets
from datetime import (
    datetime,
    timedelta,
)

import jwt
from passlib.context import (
    CryptContext,
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
)

if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY must be set in environment"
    )


JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


def generate_api_key() -> str:
    return (
        f"sp_{secrets.token_urlsafe(32)}"
    )


def hash_api_key(
    api_key: str,
) -> str:
    return hashlib.sha256(
        api_key.encode()
    ).hexdigest()


def get_key_prefix(
    api_key: str,
) -> str:
    return api_key[:12]


def hash_password(
    password: str,
) -> str:
    return pwd_context.hash(
        password
    )


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    user_id: str,
    email: str,
    role: str,
    tenant_id: str,
) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "tenant_id": tenant_id,
        "exp": datetime.utcnow()
        + timedelta(
            hours=JWT_EXPIRATION_HOURS
        ),
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def verify_access_token(
    token: str,
):
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[
                JWT_ALGORITHM
            ],
        )

        return payload

    except jwt.PyJWTError:
        return None