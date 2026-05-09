from enum import Enum


class AgentType(str, Enum):
    TRIAGE = "triage"
    SPECIALIST = "specialist"
    TONE = "tone"