from typing import Optional, Dict, Any

from app.services.redis_service import RedisService
from app.core.logging import log_info, log_error


class GraphCheckpointService:
    def __init__(self):
        self.redis_service = RedisService()

    def _checkpoint_key(self, session_id: str) -> str:
        return f"checkpoint:{session_id}"

    def save_checkpoint(
        self,
        session_id: str,
        state: Dict[str, Any],
    ) -> bool:
        try:
            success = self.redis_service.set_data(
                self._checkpoint_key(session_id),
                state,
            )

            if success:
                log_info(
                    f"Graph checkpoint saved for session {session_id}"
                )

            return success

        except Exception as e:
            log_error(
                f"Failed to save checkpoint for session {session_id}: {str(e)}"
            )
            return False

    def load_checkpoint(
        self,
        session_id: str,
    ) -> Optional[Dict[str, Any]]:
        try:
            checkpoint = self.redis_service.get_data(
                self._checkpoint_key(session_id)
            )

            return checkpoint

        except Exception as e:
            log_error(
                f"Failed to load checkpoint for session {session_id}: {str(e)}"
            )
            return None

    def clear_checkpoint(self, session_id: str) -> bool:
        try:
            success = self.redis_service.delete_data(
                self._checkpoint_key(session_id)
            )

            if success:
                log_info(
                    f"Graph checkpoint cleared for session {session_id}"
                )

            return success

        except Exception as e:
            log_error(
                f"Failed to clear checkpoint for session {session_id}: {str(e)}"
            )
            return False