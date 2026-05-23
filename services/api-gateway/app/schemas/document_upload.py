from pydantic import BaseModel


class DocumentUploadResponse(
    BaseModel
):
    job_id: str

    status: str

    document_id: str

    filename: str