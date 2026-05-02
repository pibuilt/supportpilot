from sqlalchemy.orm import Session

from app.db.models.embedding import Embedding
from app.legal.clause_detector import detect_clauses
from app.repositories.clause_analysis_repository import (
    ClauseAnalysisRepository,
)

def deduplicate_findings(findings):
    seen = set()
    unique = []

    for finding in findings:
        key = (
            finding["clause_type"],
            finding["matched_text"].lower(),
        )

        if key not in seen:
            seen.add(key)
            unique.append(finding)

    return unique

def generate_executive_summary(findings):
    high_risk = sum(
        1 for f in findings
        if f.get("risk_level") == "high"
    )

    medium_risk = sum(
        1 for f in findings
        if f.get("risk_level") == "medium"
    )

    low_risk = sum(
        1 for f in findings
        if f.get("risk_level") == "low"
    )

    critical_clauses = [
        f["clause_type"]
        for f in findings
        if f.get("risk_level") == "high"
    ]

    return {
        "overall_risk": (
            "high" if high_risk > 0
            else "medium" if medium_risk > 2
            else "low"
        ),
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
        "critical_clauses": list(set(critical_clauses)),
    }

def analyze_contract(document_id: str, db: Session):
    chunks = (
        db.query(Embedding)
        .filter(Embedding.document_id == document_id)
        .all()
    )

    all_findings = []
    summary_counts = {}

    try:
        for chunk in chunks:
            findings = detect_clauses(chunk.chunk_text)

            if findings:
                ClauseAnalysisRepository.save_clause_analyses(
                    db=db,
                    document_id=document_id,
                    chunk_id=chunk.chunk_id,
                    findings=findings,
                )

            for finding in findings:
                all_findings.append(finding)

                clause_type = finding["clause_type"]

                summary_counts[clause_type] = (
                    summary_counts.get(clause_type, 0) + 1
                )

        db.commit()

    except Exception:
        db.rollback()
        raise

    deduplicated_findings = deduplicate_findings(
        all_findings
    )

    executive_summary = generate_executive_summary(
        deduplicated_findings
    )

    return {
        "document_id": document_id,
        "clauses": deduplicated_findings,
        "summary": {
            "total_clauses": len(deduplicated_findings),
            "by_type": summary_counts,
        },
        "executive_summary": executive_summary,
    }