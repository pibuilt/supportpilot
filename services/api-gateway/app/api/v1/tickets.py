from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ticket import (
    TicketCreateRequest,
    TicketCreateResponse,
)
from app.services.ticket_service import (
    create_support_ticket,
    get_support_ticket,
    list_support_tickets,
    search_support_tickets,
)

router = APIRouter(
    prefix="/v1/tickets",
    tags=["Tickets"],
)


@router.post(
    "",
    response_model=TicketCreateResponse,
)
def create_ticket(
    payload: TicketCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    owner_id = getattr(
        request.state,
        "owner",
        None,
    )

    tenant_id = getattr(
        request.state,
        "tenant_id",
        None,
    )

    result = create_support_ticket(
        db=db,
        owner_id=owner_id,
        tenant_id=tenant_id,
        ticket_text=payload.ticket_text,
    )

    return result


@router.get("/{ticket_id}")
def get_ticket(
    ticket_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    owner_id = getattr(
        request.state,
        "owner",
        None,
    )

    tenant_id = getattr(
        request.state,
        "tenant_id",
        None,
    )

    result = get_support_ticket(
        db=db,
        owner_id=owner_id,
        tenant_id=tenant_id,
        ticket_id=ticket_id,
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return result


@router.get("")
def list_tickets(
    request: Request,
    status: str = Query(
        default=None
    ),
    limit: int = Query(
        default=20,
        le=100,
    ),
    offset: int = Query(
        default=0
    ),
    db: Session = Depends(get_db),
):
    owner_id = getattr(
        request.state,
        "owner",
        None,
    )

    tenant_id = getattr(
        request.state,
        "tenant_id",
        None,
    )

    return list_support_tickets(
        db=db,
        owner_id=owner_id,
        tenant_id=tenant_id,
        status=status,
        limit=limit,
        offset=offset,
    )


@router.get("/search/query")
def search_tickets(
    q: str,
    request: Request,
    limit: int = Query(
        default=5,
        le=20,
    ),
    db: Session = Depends(get_db),
):
    owner_id = getattr(
        request.state,
        "owner",
        None,
    )

    tenant_id = getattr(
        request.state,
        "tenant_id",
        None,
    )

    return search_support_tickets(
        db=db,
        owner_id=owner_id,
        tenant_id=tenant_id,
        query_text=q,
        limit=limit,
    )