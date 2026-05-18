from sqlalchemy.orm import (
    Session,
)

from app.db.models.api_key import (
    APIKey,
)
from app.db.models.usage_log import (
    UsageLog,
)
from app.utils.security import (
    hash_api_key,
)


class AuthService:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def validate_api_key(
        self,
        api_key: str,
    ):
        hashed = hash_api_key(
            api_key
        )

        key = (
            self.db.query(APIKey)
            .filter(
                APIKey.hashed_key
                == hashed,
                APIKey.is_active
                == True,
            )
            .first()
        )

        if not key:
            return {
                "valid": False
            }

        return {
            "valid": True,

            # Legacy compatibility
            "owner": key.owner,

            # Stable identity
            "user_id": key.user_id,

            "role": key.role,
            "tenant_id": (
                key.tenant_id
            ),
            "api_key_id": key.id,
        }

    def log_usage(
        self,
        api_key_id: str,
        tenant_id: str,
        endpoint: str,
        status_code: int,
        tokens_used: int = 0,
    ):
        usage = UsageLog(
            api_key_id=api_key_id,
            tenant_id=tenant_id,
            endpoint=endpoint,
            status_code=status_code,
            tokens_used=tokens_used,
        )

        self.db.add(usage)
        self.db.commit()