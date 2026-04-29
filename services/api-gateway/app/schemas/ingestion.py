from pydantic import BaseModel


class DocumentIngestRequest(BaseModel):
    document_id: str
    text: str