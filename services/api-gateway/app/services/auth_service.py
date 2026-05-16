from sqlalchemy.orm import Session

from app.db.models.api_key import APIKey
from app.utils.security import (
    generate_api_key,
    hash_api_key,
    get_key_prefix,
)


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def create_api_key(
        self,
        owner: str,
        role: str,
        tenant_id: str,
    ):
        raw_key = generate_api_key()

        db_key = APIKey(
            key_prefix=get_key_prefix(raw_key),
            hashed_key=hash_api_key(raw_key),
            owner=owner,
            role=role,
            tenant_id=tenant_id,
            is_active=True,
        )

        self.db.add(db_key)
        self.db.commit()
        self.db.refresh(db_key)

        return {
            "api_key": raw_key,
            "key_prefix": db_key.key_prefix,
            "owner": db_key.owner,
            "role": db_key.role,
            "tenant_id": db_key.tenant_id,
        }

    def validate_api_key(
        self,
        api_key: str,
    ):
        hashed = hash_api_key(api_key)

        key = (
            self.db.query(APIKey)
            .filter(
                APIKey.hashed_key == hashed,
                APIKey.is_active == True,
            )
            .first()
        )

        if not key:
            return {
                "valid": False
            }

        return {
            "valid": True,
            "owner": key.owner,
            "role": key.role,
            "tenant_id": key.tenant_id,
        }