from sqlalchemy.orm import Session

from app.services.triage_service import TriageService
from app.services.specialist_service import SpecialistService
from app.services.tone_service import ToneService


class OrchestrationService:
    def __init__(self):
        self.triage_service = TriageService()
        self.specialist_service = SpecialistService()
        self.tone_service = ToneService()

    def process(
        self,
        db: Session,
        document_id: str,
        query: str,
    ):
        triage_result = self.triage_service.process(query)

        specialist_result = self.specialist_service.process(
            db=db,
            document_id=document_id,
            query=query,
        )

        tone_result = self.tone_service.process(
            db=db,
            document_id=document_id,
            query=query,
        )

        return {
            "triage": triage_result,
            "specialist": specialist_result,
            "tone": tone_result,
        }