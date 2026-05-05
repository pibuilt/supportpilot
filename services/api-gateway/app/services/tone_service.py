from sqlalchemy.orm import Session

from app.services.specialist_service import SpecialistService
from app.agents.tone_agent import ToneAgent


class ToneService:
    def __init__(self):
        self.specialist = SpecialistService()
        self.tone_agent = ToneAgent()

    def process(
        self,
        db: Session,
        document_id: str,
        query: str,
    ):
        specialist_output = self.specialist.process(
            db=db,
            document_id=document_id,
            query=query,
        )

        refined_output = self.tone_agent.refine(
            summary=specialist_output["summary"],
            risks=specialist_output["risks"],
            recommendations=specialist_output["recommendations"],
        )

        return {
            "executive_summary": refined_output["executive_summary"],
            "business_risks": refined_output["business_risks"],
            "recommended_actions": refined_output["recommended_actions"],
        }