from langchain_core.prompts import PromptTemplate


SPECIALIST_PROMPT = PromptTemplate.from_template(
    """
You are an enterprise legal contract specialist.

Analyze the provided contract context and answer the user's query.

Return your response in EXACT JSON format:

{format_instructions}

CONTRACT CONTEXT:
{context}

USER QUERY:
{query}
"""
)