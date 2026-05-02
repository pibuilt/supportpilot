from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# CREATE
class TicketCreateRequest(BaseModel):
    ticket_text: str


class TicketCreateResponse(BaseModel):
    ticket_id: str
    status: str
    message: str


# GET SINGLE
class TicketResponse(BaseModel):
    ticket_id: str
    ticket_text: str
    status: str
    created_at: datetime
    updated_at: datetime


# LIST ITEM
class TicketListItem(BaseModel):
    ticket_id: str
    ticket_text: str
    status: str
    created_at: datetime


# LIST RESPONSE
class TicketListResponse(BaseModel):
    total: int
    count: int
    tickets: List[TicketListItem]


# SEARCH RESPONSE
class TicketSearchResponse(BaseModel):
    query: str
    count: int
    tickets: List[TicketListItem]