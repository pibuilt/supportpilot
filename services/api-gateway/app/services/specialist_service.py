from sqlalchemy.orm import Session

from app.services.retrieval_service import search_documents
from app.agents.specialist_agent import SpecialistAgent
from app.utils.legal_output_parser import parse_legal_output

class SpecialistService:
    def __init__(self):
        self.agent = SpecialistAgent()

    def process(
        self,
        db: Session,
        document_id: str,
        query: str,
    ):
        search_output = search_documents(
            db=db,
            query=query,
            document_id=document_id,
            top_k=5,
        )

        results = search_output["results"]

        context = "\n\n".join(
            [
                result["chunk_text"]
                for result in results
                if result.get("chunk_text")
            ]
        )

        llm_output = self.agent.analyze(
            context=context,
            query=query,
        )

        parsed_output = parse_legal_output(llm_output)

        return parsed_output