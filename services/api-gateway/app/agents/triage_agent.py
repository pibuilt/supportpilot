import re
from app.agents.base_agent import BaseAgent
from app.agents.types import AgentResult


class TriageAgent(BaseAgent):
    CONTRACT_PATTERNS = {
        "nda": [r"\bnon-disclosure\b", r"\bconfidential\b", r"\bnda\b"],
        "employment": [r"\bemployment\b", r"\bemployee\b", r"\bemployer\b"],
        "saas": [r"\bsubscription\b", r"\bservice level\b", r"\bsaas\b"],
        "vendor": [r"\bvendor\b", r"\bsupplier\b", r"\bprocurement\b"],
        "lease": [r"\blease\b", r"\blandlord\b", r"\btenant\b"],
    }

    LEGAL_AREAS = {
        "termination": [r"\btermination\b", r"\bterminate\b"],
        "liability": [r"\bliability\b", r"\bindemnity\b"],
        "payment": [r"\bpayment\b", r"\bfees\b", r"\binvoice\b"],
        "privacy": [r"\bprivacy\b", r"\bdata protection\b"],
    }

    def execute(self, input_data):
        text = input_data.lower()

        document_type, doc_score = self._classify_document(text)
        legal_area, legal_score = self._classify_legal_area(text)

        confidence = round(max(doc_score, legal_score), 2)

        clarification_questions = self._detect_missing_context(text)

        return AgentResult(
            document_type=document_type,
            legal_area=legal_area,
            risk_level=self._risk_level(confidence),
            confidence_score=confidence,
            recommended_agent=self._recommend_agent(legal_area),
            clarification_needed=len(clarification_questions) > 0,
            clarification_questions=clarification_questions,
        )

    def _classify_document(self, text):
        best_match = ("general", 0.5)

        for doc_type, patterns in self.CONTRACT_PATTERNS.items():
            score = sum(bool(re.search(pattern, text)) for pattern in patterns)
            if score > best_match[1]:
                best_match = (doc_type, min(1.0, score / len(patterns)))

        return best_match

    def _classify_legal_area(self, text):
        best_match = ("general", 0.5)

        for area, patterns in self.LEGAL_AREAS.items():
            score = sum(bool(re.search(pattern, text)) for pattern in patterns)
            if score > best_match[1]:
                best_match = (area, min(1.0, score / len(patterns)))

        return best_match

    def _detect_missing_context(self, text):
        questions = []

        if "governing law" not in text:
            questions.append("What governing law or jurisdiction applies?")

        if "termination" not in text:
            questions.append("Are termination provisions included?")

        if "payment" not in text:
            questions.append("What payment obligations exist?")

        return questions

    def _risk_level(self, confidence):
        if confidence >= 0.85:
            return "high"
        elif confidence >= 0.7:
            return "medium"
        return "low"

    def _recommend_agent(self, legal_area):
        return f"{legal_area}_specialist"