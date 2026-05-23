from sqlalchemy.orm import Session

from app.db.models.chat_message import (
    ChatMessage,
)


class ChatMessageRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        session_id: str,
        owner_id: str,
        tenant_id: str,
        role: str,
        content: str,
    ):
        message = ChatMessage(
            session_id=session_id,
            owner_id=owner_id,
            tenant_id=tenant_id,
            role=role,
            content=content,
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    def get_session_messages(
        self,
        session_id: str,
        owner_id: str,
        tenant_id: str,
        limit: int,
        offset: int,
    ):
        return (
            self.db.query(
                ChatMessage
            )
            .filter(
                ChatMessage.session_id
                == session_id,
                ChatMessage.owner_id
                == owner_id,
                ChatMessage.tenant_id
                == tenant_id,
            )
            .order_by(
                ChatMessage.created_at.asc()
            )
            .offset(offset)
            .limit(limit)
            .all()
        )
    
    def count_messages(
        self,
        session_id: str,
    ):
        return (
            self.db.query(
                ChatMessage
            )
            .filter(
                ChatMessage.session_id
                == session_id
            )
            .count()
        )