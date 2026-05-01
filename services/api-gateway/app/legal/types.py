from enum import Enum


class ClauseType(str, Enum):
    TERMINATION = "termination"
    LIABILITY = "liability"
    INDEMNIFICATION = "indemnification"
    CONFIDENTIALITY = "confidentiality"
    COMPLIANCE = "compliance"