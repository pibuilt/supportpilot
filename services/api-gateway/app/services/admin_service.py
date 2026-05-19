from app.db.models.api_key import (
    APIKey,
)

from app.db.models.user import (
    User,
)

from app.utils.security import (
    generate_api_key,
    get_key_prefix,
    hash_api_key,
)


class AdminService:

    @staticmethod
    def promote_to_admin(
        user: User,
    ):
        user.role = "admin"

    @staticmethod
    def demote_to_user(
        user: User,
    ):
        user.role = "user"

    @staticmethod
    def revoke_api_key(
        api_key: APIKey,
    ):
        api_key.is_active = False

    @staticmethod
    def regenerate_api_key(
        api_key: APIKey,
    ):
        raw_key = (
            generate_api_key()
        )

        api_key.key_prefix = (
            get_key_prefix(
                raw_key
            )
        )

        api_key.hashed_key = (
            hash_api_key(
                raw_key
            )
        )

        api_key.is_active = True

        return raw_key