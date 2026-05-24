from sqlalchemy.orm import Session

from app.db.models.chat_session import (
    ChatSession,
)

from app.db.models.chat_message import (
    ChatMessage,
)


class ChatExportRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def list_sessions(
        self,
        owner_id: str,
        tenant_id: str,
    ):
        return (
            self.db.query(
                ChatSession
            )
            .filter(
                ChatSession.owner_id
                == owner_id,
                ChatSession.tenant_id
                == tenant_id,
            )
            .all()
        )

    def get_messages(
        self,
        session_id: str,
    ):
        return (
            self.db.query(
                ChatMessage
            )
            .filter(
                ChatMessage.session_id
                == session_id,
            )
            .order_by(
                ChatMessage.created_at
            )
            .all()
        )