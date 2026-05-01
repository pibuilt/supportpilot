from sqlalchemy.orm import Session

from app.db.models.embedding import Embedding
from app.legal.clause_detector import detect_clauses
from app.repositories.clause_analysis_repository import (
    ClauseAnalysisRepository,
)


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

    return {
        "document_id": document_id,
        "clauses": all_findings,
        "summary": {
            "total_clauses": len(all_findings),
            "by_type": summary_counts,
        },
    }