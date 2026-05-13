from typing import List, Dict, Optional

from app.services.redis_service import RedisService
from app.core.logging import log_info, log_error


class MemoryService:
    def __init__(self):
        self.redis_service = RedisService()

    def _session_key(self, session_id: str) -> str:
        return f"session:{session_id}"

    def load_session(self, session_id: str) -> List[Dict]:
        try:
            history = self.redis_service.get_data(
                self._session_key(session_id)
            )

            if history is None:
                return []

            return history

        except Exception as e:
            log_error(
                f"Failed to load session memory for {session_id}: {str(e)}"
            )
            return []

    def save_session(
        self,
        session_id: str,
        history: List[Dict],
    ) -> bool:
        try:
            success = self.redis_service.set_data(
                self._session_key(session_id),
                history,
            )

            if success:
                log_info(
                    f"Session memory saved successfully for {session_id}"
                )

            return success

        except Exception as e:
            log_error(
                f"Failed to save session memory for {session_id}: {str(e)}"
            )
            return False

    def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> bool:
        try:
            history = self.load_session(session_id)

            history.append(
                {
                    "role": role,
                    "content": content,
                }
            )

            return self.save_session(
                session_id,
                history,
            )

        except Exception as e:
            log_error(
                f"Failed to append message for session {session_id}: {str(e)}"
            )
            return False

    def clear_session(self, session_id: str) -> bool:
        try:
            success = self.redis_service.delete_data(
                self._session_key(session_id)
            )

            if success:
                log_info(
                    f"Session memory cleared for {session_id}"
                )

            return success

        except Exception as e:
            log_error(
                f"Failed to clear session {session_id}: {str(e)}"
            )
            return False