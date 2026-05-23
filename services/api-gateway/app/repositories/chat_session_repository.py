from sqlalchemy.orm import Session

from app.db.models.chat_session import (
    ChatSession,
)


class ChatSessionRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def get_by_id(
        self,
        session_id: str,
    ):
        return (
            self.db.query(
                ChatSession
            )
            .filter(
                ChatSession.id
                == session_id
            )
            .first()
        )

    def create(
        self,
        session_id: str,
        owner_id: str,
        tenant_id: str,
        title: str | None = None,
    ):
        session = ChatSession(
            id=session_id,
            owner_id=owner_id,
            tenant_id=tenant_id,
            title=title,
            message_count=0,
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    def get_or_create(
        self,
        session_id: str,
        owner_id: str,
        tenant_id: str,
    ):
        existing = self.get_by_id(
            session_id
        )

        if existing:
            return existing

        return self.create(
            session_id=session_id,
            owner_id=owner_id,
            tenant_id=tenant_id,
        )

    def increment_message_count(
        self,
        session_id: str,
        amount: int = 1,
    ):
        session = (
            self.get_by_id(
                session_id
            )
        )

        if not session:
            return None

        session.message_count += amount

        self.db.commit()
        self.db.refresh(session)

        return session

    def list_sessions(
        self,
        owner_id: str,
        tenant_id: str,
        limit: int,
        offset: int,
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
            .order_by(
                ChatSession.updated_at.desc()
            )
            .offset(offset)
            .limit(limit)
            .all()
        )