from fastapi import (
    APIRouter,
    Depends,
    Request,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.repositories.chat_session_repository import (
    ChatSessionRepository,
)

from app.repositories.chat_message_repository import (
    ChatMessageRepository,
)


router = APIRouter(
    prefix="/v1/sessions",
    tags=["Sessions"],
)


@router.get("")
def list_sessions(
    request: Request,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    owner_id = request.state.owner

    tenant_id = (
        request.state.tenant_id
    )

    session_repo = (
        ChatSessionRepository(db)
    )

    sessions = (
        session_repo.list_sessions(
            owner_id=owner_id,
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
        )
    )

    return {
        "items": [
            {
                "id": s.id,
                "title": s.title,
                "message_count": (
                    s.message_count
                ),
                "created_at": (
                    s.created_at
                ),
                "updated_at": (
                    s.updated_at
                ),
            }
            for s in sessions
        ]
    }


@router.get("/{session_id}")
def get_session(
    session_id: str,
    request: Request,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    owner_id = request.state.owner

    tenant_id = (
        request.state.tenant_id
    )

    session_repo = (
        ChatSessionRepository(db)
    )

    message_repo = (
        ChatMessageRepository(db)
    )

    session = (
        session_repo.get_owned_session(
            session_id=session_id,
            owner_id=owner_id,
            tenant_id=tenant_id,
        )
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    messages = (
        message_repo.get_session_messages(
            session_id=session_id,
            owner_id=owner_id,
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
        )
    )

    return {
        "id": session.id,
        "title": session.title,
        "message_count": (
            session.message_count
        ),
        "created_at": (
            session.created_at
        ),
        "updated_at": (
            session.updated_at
        ),
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": (
                    m.created_at
                ),
            }
            for m in messages
        ],
    }