HIGH_PRIORITY_TERMS = [
    "urgent",
    "immediately",
    "critical",
    "security",
    "breach",
    "down",
    "failure",
]

MEDIUM_PRIORITY_TERMS = [
    "issue",
    "problem",
    "error",
    "refund",
    "delayed",
]


def assign_ticket_priority(ticket_text: str) -> str:
    text = ticket_text.lower()

    for term in HIGH_PRIORITY_TERMS:
        if term in text:
            return "high"

    for term in MEDIUM_PRIORITY_TERMS:
        if term in text:
            return "medium"

    return "low"