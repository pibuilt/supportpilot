from app.services.llm_client import OllamaClient


class SpecialistAgent:
    def __init__(self):
        self.llm = OllamaClient()

    def analyze(self, context: str, query: str) -> str:
        prompt = f"""
You are an enterprise legal contract analysis specialist.

Analyze the following contract excerpts and answer the user's legal question.

USER QUERY:
{query}

CONTRACT CONTEXT:
{context}

Provide:

1. Summary
2. Key Risks
3. Recommendations

Use concise legal language.
"""

        return self.llm.generate(prompt)