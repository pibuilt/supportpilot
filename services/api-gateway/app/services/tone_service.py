from sqlalchemy.orm import Session

from app.services.specialist_service import SpecialistService
from app.agents.tone_agent import ToneAgent
from app.utils.legal_output_parser import parse_legal_output


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

        parsed_tone_output = parse_legal_output(refined_output)

        return {
            "executive_summary": parsed_tone_output["summary"],
            "business_risks": parsed_tone_output["risks"],
            "recommended_actions": parsed_tone_output["recommendations"],
        }