from app.repositories.ticket_repository import TicketRepository
from app.services.ticket_classifier import classify_ticket
from app.services.ticket_priority import assign_ticket_priority

def create_support_ticket(db, ticket_text: str):
    repository = TicketRepository(db)

    category = classify_ticket(ticket_text)
    priority = assign_ticket_priority(ticket_text)

    ticket = repository.create_ticket(
        ticket_text=ticket_text,
        status="open",
        category=category,
        priority=priority,
    )

    return {
        "ticket_id": ticket.id,
        "status": ticket.status,
        "category": category,
        "priority": priority,
        "message": "Support ticket created successfully"
    }

def get_support_ticket(db, ticket_id: str):
    repository = TicketRepository(db)

    ticket = repository.get_ticket_by_id(ticket_id)

    if not ticket:
        return None

    return {
        "ticket_id": ticket.id,
        "ticket_text": ticket.ticket_text,
        "status": ticket.status,
        "category": ticket.category,
        "priority": ticket.priority,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at
    }


def list_support_tickets(
    db,
    status: str = None,
    limit: int = 20,
    offset: int = 0
):
    repository = TicketRepository(db)

    tickets, total = repository.list_tickets(
        status=status,
        limit=limit,
        offset=offset
    )

    return {
        "total": total,
        "count": len(tickets),
        "tickets": [
            {
                "ticket_id": ticket.id,
                "ticket_text": ticket.ticket_text,
                "status": ticket.status,
                "category": ticket.category,
                "priority": ticket.priority,
                "created_at": ticket.created_at
            }
            for ticket in tickets
        ]
    }


def search_support_tickets(
    db,
    query_text: str,
    limit: int = 5
):
    repository = TicketRepository(db)

    tickets = repository.search_tickets(
        query_text=query_text,
        limit=limit
    )

    return {
        "query": query_text,
        "count": len(tickets),
        "tickets": [
            {
                "ticket_id": ticket.id,
                "ticket_text": ticket.ticket_text,
                "status": ticket.status,
                "category": ticket.category,
                "priority": ticket.priority,
            }
            for ticket in tickets
        ]
    }