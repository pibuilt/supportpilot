from pydantic import BaseModel


class TicketCreate(BaseModel):
    ticket_text: str
    status: str = "open"


class TicketResponse(BaseModel):
    ticket_id: str
    status: str
    ticket_text: str