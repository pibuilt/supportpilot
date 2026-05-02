from app.db.models.ticket import Ticket
from sqlalchemy.orm import Session


class TicketRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_ticket(self, ticket_text: str, status: str):
        ticket = Ticket(
            ticket_text=ticket_text,
            status=status
        )

        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def get_ticket_by_id(self, ticket_id: str):
        return (
            self.db.query(Ticket)
            .filter(Ticket.id == ticket_id)
            .first()
        )

    def list_tickets(
        self,
        status: str = None,
        limit: int = 20,
        offset: int = 0
    ):
        query = self.db.query(Ticket)

        if status:
            query = query.filter(Ticket.status == status)

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
        query_text: str,
        limit: int = 5
    ):
        tickets = (
            self.db.query(Ticket)
            .filter(Ticket.ticket_text.ilike(f"%{query_text}%"))
            .limit(limit)
            .all()
        )

        return tickets