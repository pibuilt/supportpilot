import re
from app.legal.patterns import CLAUSE_PATTERNS


def detect_clauses(text: str):

    if not text:
        return []
    
    findings = []

    for clause_type, patterns in CLAUSE_PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                findings.append(
                    {
                        "clause_type": clause_type,
                        "matched_text": match.group(),
                        "confidence_score": 0.8,
                        "metadata": {
                            "pattern": pattern,
                            "start": match.start(),
                            "end": match.end(),
                        },
                    }
                )

    return findings