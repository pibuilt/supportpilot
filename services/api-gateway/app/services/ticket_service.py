from app.repositories.ticket_repository import TicketRepository


def create_support_ticket(db, ticket_text: str, status: str = "open"):
    repository = TicketRepository(db)

    ticket = repository.create_ticket(
        ticket_text=ticket_text,
        status=status
    )

    return {
        "ticket_id": ticket.id,
        "status": ticket.status,
        "ticket_text": ticket.ticket_text
    }