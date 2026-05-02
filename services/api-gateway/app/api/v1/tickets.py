from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ticket import TicketCreate
from app.services.ticket_service import create_support_ticket

router = APIRouter()


@router.post("/tickets")
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    return create_support_ticket(
        db=db,
        ticket_text=payload.ticket_text,
        status=payload.status
    )