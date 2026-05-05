from langchain_core.prompts import PromptTemplate


TONE_PROMPT = PromptTemplate.from_template(
    """
You are an enterprise legal communications specialist.

Refine the legal analysis below into:
- concise
- executive-safe
- professional
- boardroom-ready communication

Return your response in EXACT JSON format:

{format_instructions}

LEGAL SUMMARY:
{summary}

LEGAL RISKS:
{risks}

LEGAL RECOMMENDATIONS:
{recommendations}
"""
)