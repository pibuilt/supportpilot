from sqlalchemy.orm import (
    Session,
)

from app.db.models.api_key import (
    APIKey,
)
from app.db.models.user import (
    User,
)
from app.utils.security import (
    create_access_token,
    generate_api_key,
    get_key_prefix,
    hash_api_key,
    hash_password,
    verify_password,
)


class UserAuthService:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def _create_user_api_key(
        self,
        user_id: str,
        full_name: str,
        role: str,
        tenant_id: str,
    ):
        raw_key = (
            generate_api_key()
        )

        db_key = APIKey(
            key_prefix=get_key_prefix(
                raw_key
            ),
            hashed_key=hash_api_key(
                raw_key
            ),

            # Legacy compatibility
            owner=full_name,

            # Stable identity
            user_id=user_id,

            role=role,
            tenant_id=tenant_id,
            is_active=True,
        )

        self.db.add(db_key)
        self.db.commit()
        self.db.refresh(db_key)

        return {
            "api_key": raw_key,
            "key_prefix": (
                db_key.key_prefix
            ),
        }

    def signup(
        self,
        email: str,
        password: str,
        full_name: str,
        tenant_id: str,
        role: str = "user",
    ):
        existing_user = (
            self.db.query(User)
            .filter(
                User.email
                == email
            )
            .first()
        )

        if existing_user:
            raise ValueError(
                "User already exists"
            )

        existing_admin = (
            self.db.query(User)
            .filter(
                User.role.in_(
                    [
                        "admin",
                        "root_admin",
                    ]
                )
            )
            .count()
        )

        # Bootstrap first-ever platform admin
        if existing_admin == 0:
            role = "root_admin"

        # Block unauthorized admin creation after bootstrap
        elif role in [
            "admin",
            "root_admin",
        ]:
            raise ValueError(
                "Only existing admins can create admin users"
            )

        user = User(
            email=email,
            hashed_password=hash_password(
                password
            ),
            full_name=full_name,
            tenant_id=tenant_id,
            role=role,
            is_active=True,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        api_key_data = (
            self._create_user_api_key(
                user_id=user.id,
                full_name=user.full_name,
                role=user.role,
                tenant_id=user.tenant_id,
            )
        )

        token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
            tenant_id=user.tenant_id,
        )

        return {
            "access_token": token,
            "api_key": api_key_data[
                "api_key"
            ],
            "key_prefix": api_key_data[
                "key_prefix"
            ],
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "tenant_id": user.tenant_id,
        }

    def login(
        self,
        email: str,
        password: str,
    ):
        user = (
            self.db.query(User)
            .filter(
                User.email
                == email,
                User.is_active
                == True,
            )
            .first()
        )

        if not user:
            raise ValueError(
                "Invalid credentials"
            )

        if not verify_password(
            password,
            user.hashed_password,
        ):
            raise ValueError(
                "Invalid credentials"
            )

        existing_key = (
            self.db.query(APIKey)
            .filter(
                APIKey.user_id
                == user.id,
                APIKey.tenant_id
                == user.tenant_id,
                APIKey.is_active
                == True,
            )
            .first()
        )

        if not existing_key:
            api_key_data = (
                self._create_user_api_key(
                    user_id=user.id,
                    full_name=user.full_name,
                    role=user.role,
                    tenant_id=user.tenant_id,
                )
            )
        else:
            api_key_data = {
                "api_key": "Use existing key securely stored",
                "key_prefix": existing_key.key_prefix,
            }

        token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
            tenant_id=user.tenant_id,
        )

        return {
            "access_token": token,
            "api_key": api_key_data[
                "api_key"
            ],
            "key_prefix": api_key_data[
                "key_prefix"
            ],
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "tenant_id": user.tenant_id,
        }

    def get_current_user(
        self,
        user_id: str,
    ):
        user = (
            self.db.query(User)
            .filter(
                User.id
                == user_id,
                User.is_active
                == True,
            )
            .first()
        )

        if not user:
            return None

        return {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "tenant_id": user.tenant_id,
            "is_active": user.is_active,
        }