from app.agents.triage_agent import TriageAgent


class TriageService:
    def __init__(self):
        self.agent = TriageAgent()

    def process(self, document_text: str):
        return self.agent.execute(document_text)