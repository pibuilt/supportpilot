from app.services.llm_client import OllamaClient


class ToneAgent:
    def __init__(self):
        self.llm = OllamaClient()

    def refine(
        self,
        summary: str,
        risks: str,
        recommendations: str,
    ) -> str:
        prompt = f"""
You are an enterprise legal communications specialist.

Rewrite the following legal analysis into:

1. Summary
2. Key Risks
3. Recommendations

Requirements:
- concise
- professional
- boardroom-ready
- customer-safe
- avoid repetition
- preserve legal meaning

LEGAL SUMMARY:
{summary}

LEGAL RISKS:
{risks}

LEGAL RECOMMENDATIONS:
{recommendations}
"""

        return self.llm.generate(prompt)