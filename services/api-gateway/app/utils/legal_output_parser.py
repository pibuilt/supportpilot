import re


def parse_legal_output(raw_output: str) -> dict:
    summary = ""
    risks = ""
    recommendations = ""

    summary_match = re.search(
        r"1\.\s*Summary:(.*?)(?=2\.\s*Key Risks:|$)",
        raw_output,
        re.DOTALL | re.IGNORECASE,
    )

    risks_match = re.search(
        r"2\.\s*Key Risks:(.*?)(?=3\.\s*Recommendations:|$)",
        raw_output,
        re.DOTALL | re.IGNORECASE,
    )

    recommendations_match = re.search(
        r"3\.\s*Recommendations:(.*)",
        raw_output,
        re.DOTALL | re.IGNORECASE,
    )

    if summary_match:
        summary = summary_match.group(1).strip()

    if risks_match:
        risks = risks_match.group(1).strip()

    if recommendations_match:
        recommendations = recommendations_match.group(1).strip()

    return {
        "summary": summary,
        "risks": risks,
        "recommendations": recommendations,
    }