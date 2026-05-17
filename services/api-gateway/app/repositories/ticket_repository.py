from app.db.models.ticket import Ticket
from sqlalchemy.orm import Session


class TicketRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_ticket(
        self,
        owner_id: str,
        tenant_id: str,
        ticket_text: str,
        status: str,
        category: str,
        priority: str,
    ):
        ticket = Ticket(
            owner_id=owner_id,
            tenant_id=tenant_id,
            ticket_text=ticket_text,
            status=status,
            category=category,
            priority=priority,
        )

        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def get_ticket_by_id(
        self,
        owner_id: str,
        tenant_id: str,
        ticket_id: str,
    ):
        return (
            self.db.query(Ticket)
            .filter(
                Ticket.id == ticket_id,
                Ticket.owner_id == owner_id,
                Ticket.tenant_id == tenant_id,
            )
            .first()
        )

    def list_tickets(
        self,
        owner_id: str,
        tenant_id: str,
        status: str = None,
        limit: int = 20,
        offset: int = 0,
    ):
        query = (
            self.db.query(Ticket)
            .filter(
                Ticket.owner_id == owner_id,
                Ticket.tenant_id == tenant_id,
            )
        )

        if status:
            query = query.filter(
                Ticket.status == status
            )

        total = query.count()

        tickets = (
            query.order_by(Ticket.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return tickets, total

    def search_tickets(
        self,
        owner_id: str,
        tenant_id: str,
        query_text: str,
        limit: int = 5,
    ):
        tickets = (
            self.db.query(Ticket)
            .filter(
                Ticket.owner_id == owner_id,
                Ticket.tenant_id == tenant_id,
                Ticket.ticket_text.ilike(
                    f"%{query_text}%"
                ),
            )
            .limit(limit)
            .all()
        )

        return tickets