import re
from app.legal.patterns import CLAUSE_PATTERNS


def determine_risk_level(clause_type: str, clause_text: str) -> str:
    text = clause_text.lower()

    high_risk_terms = [
        "unlimited liability",
        "sole discretion",
        "automatic renewal",
        "irrevocable",
        "perpetual",
        "waive rights",
        "indemnify",
        "penalty",
        "exclusive jurisdiction",
    ]

    medium_risk_terms = [
        "termination",
        "breach",
        "confidential",
        "compliance",
        "fees",
        "governing law",
        "arbitration",
    ]

    for term in high_risk_terms:
        if term in text:
            return "high"

    for term in medium_risk_terms:
        if term in text:
            return "medium"

    if clause_type in [
        "liability",
        "indemnification",
        "data_privacy",
        "intellectual_property",
    ]:
        return "medium"

    return "low"


def calculate_confidence_score(
    clause_type: str,
    matched_text: str,
    full_text: str,
) -> float:
    score = 0.75

    if len(matched_text) > 8:
        score += 0.05

    if clause_type in [
        "liability",
        "indemnification",
        "termination",
        "data_privacy",
    ]:
        score += 0.1

    if matched_text.lower() in full_text.lower():
        score += 0.05

    return round(min(score, 0.99), 2)


def detect_clauses(text: str):
    if not text:
        return []

    findings = []

    for clause_type, patterns in CLAUSE_PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(
                pattern,
                text,
                re.IGNORECASE,
            )

            for match in matches:
                findings.append(
                    {
                        "clause_type": clause_type,
                        "matched_text": match.group(),
                        "confidence_score": calculate_confidence_score(
                            clause_type,
                            match.group(),
                            text,
                        ),
                        "risk_level": determine_risk_level(
                            clause_type,
                            text,
                        ),
                        "metadata": {
                            "pattern": pattern,
                            "start": match.start(),
                            "end": match.end(),
                        },
                    }
                )

    return findings