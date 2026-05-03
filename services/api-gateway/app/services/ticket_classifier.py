TICKET_CATEGORIES = {
    "billing": [
        "refund",
        "payment",
        "invoice",
        "charge",
        "subscription",
    ],
    "technical_support": [
        "bug",
        "error",
        "issue",
        "crash",
        "login",
        "access",
    ],
    "account_management": [
        "account",
        "password",
        "reset",
        "username",
        "profile",
    ],
    "compliance": [
        "privacy",
        "gdpr",
        "security",
        "legal",
        "compliance",
    ],
    "feature_request": [
        "feature",
        "request",
        "improvement",
        "enhancement",
    ],
}


def classify_ticket(ticket_text: str) -> str:
    text = ticket_text.lower()

    for category, keywords in TICKET_CATEGORIES.items():
        for keyword in keywords:
            if keyword in text:
                return category

    return "general"