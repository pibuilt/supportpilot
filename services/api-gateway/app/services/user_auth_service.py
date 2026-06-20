from sqlalchemy.orm import (
    Session,
)

from app.constants.audit_events import (
    LOGIN_FAILED,
    LOGIN_SUCCESS,
    USER_CREATED,
)

from app.db.models.api_key import (
    APIKey,
)
from app.db.models.user import (
    User,
)
from app.services.audit_service import (
    AuditService,
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
            "api_key_id": db_key.id,
            "key_prefix": (
                db_key.key_prefix
            ),
        }

    def list_user_api_keys(
        self,
        user_id: str,
        tenant_id: str,
    ):
        keys = (
            self.db.query(APIKey)
            .filter(
                APIKey.user_id == user_id,
                APIKey.tenant_id == tenant_id,
            )
            .order_by(
                APIKey.created_at.desc()
            )
            .all()
        )

        return [
            {
                "api_key_id": key.id,
                "key_prefix": key.key_prefix,
                "owner": key.owner,
                "role": key.role,
                "tenant_id": key.tenant_id,
                "is_active": key.is_active,
                "created_at": key.created_at,
            }
            for key in keys
        ]

    def create_additional_api_key(
        self,
        user_id: str,
    ):
        user = (
            self.db.query(User)
            .filter(
                User.id == user_id,
                User.is_active == True,
            )
            .first()
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        return self._create_user_api_key(
            user_id=user.id,
            full_name=user.full_name,
            role=user.role,
            tenant_id=user.tenant_id,
        )

    def revoke_user_api_key(
        self,
        user_id: str,
        tenant_id: str,
        api_key_id: str,
    ):
        api_key = (
            self.db.query(APIKey)
            .filter(
                APIKey.id == api_key_id,
                APIKey.user_id == user_id,
                APIKey.tenant_id == tenant_id,
            )
            .first()
        )

        if not api_key:
            raise ValueError(
                "API key not found"
            )

        api_key.is_active = False
        self.db.commit()
        self.db.refresh(api_key)
        return api_key

    def regenerate_user_api_key(
        self,
        user_id: str,
        tenant_id: str,
        api_key_id: str,
    ):
        api_key = (
            self.db.query(APIKey)
            .filter(
                APIKey.id == api_key_id,
                APIKey.user_id == user_id,
                APIKey.tenant_id == tenant_id,
            )
            .first()
        )

        if not api_key:
            raise ValueError(
                "API key not found"
            )

        raw_key = (
            generate_api_key()
        )

        api_key.key_prefix = (
            get_key_prefix(raw_key)
        )
        api_key.hashed_key = (
            hash_api_key(raw_key)
        )
        api_key.is_active = True

        self.db.commit()
        self.db.refresh(api_key)

        return {
            "api_key": raw_key,
            "api_key_id": api_key.id,
            "key_prefix": api_key.key_prefix,
        }

    def signup(
        self,
        email: str,
        password: str,
        full_name: str,
        tenant_id: str,
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

        # First user on the entire platform
        if existing_admin == 0:

            role = "root_admin"

        else:

            tenant_admin_count = (
                self.db.query(User)
                .filter(
                    User.tenant_id
                    == tenant_id,

                    User.role.in_(
                        [
                            "admin",
                            "root_admin",
                        ]
                    ),
                )
                .count()
            )

            # First admin for this tenant
            if tenant_admin_count == 0:
                role = "admin"

            # Everybody else
            else:
                role = "user"

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

        AuditService.log_event(
            self.db,
            tenant_id=user.tenant_id,
            user_id=user.id,
            event_type=USER_CREATED,
            action="user_signup",
            status="success",
            resource_type="user",
            resource_id=user.id,
            event_metadata={
                "email": user.email,
                "role": user.role,
            },
        )

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

            AuditService.log_event(
                self.db,
                tenant_id="unknown",
                event_type=LOGIN_FAILED,
                action="login_attempt",
                status="failed",
                resource_type="user",
                resource_id=email,
                event_metadata={
                    "reason": "user_not_found",
                    "email": email,
                },
            )

            raise ValueError(
                "Invalid credentials"
            )

        if not verify_password(
            password,
            user.hashed_password,
        ):

            AuditService.log_event(
                self.db,
                tenant_id=user.tenant_id,
                user_id=user.id,
                event_type=LOGIN_FAILED,
                action="login_attempt",
                status="failed",
                resource_type="user",
                resource_id=user.id,
                event_metadata={
                    "reason": "invalid_password",
                    "email": user.email,
                },
            )

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

        token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
            tenant_id=user.tenant_id,
        )

        AuditService.log_event(
            self.db,
            tenant_id=user.tenant_id,
            user_id=user.id,
            event_type=LOGIN_SUCCESS,
            action="user_login",
            status="success",
            resource_type="user",
            resource_id=user.id,
            event_metadata={
                "email": user.email,
                "role": user.role,
            },
        )

        return {
            "access_token": token,
            "api_key": "",
            "key_prefix": (
                existing_key.key_prefix
                if existing_key
                else ""
            ),
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
