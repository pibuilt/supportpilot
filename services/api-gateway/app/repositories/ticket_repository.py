from app.db.models.ticket import Ticket


class TicketRepository:
    def __init__(self, db):
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