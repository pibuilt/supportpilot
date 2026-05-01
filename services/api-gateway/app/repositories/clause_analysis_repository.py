from sqlalchemy.orm import Session

from app.db.models.clause_analysis import ClauseAnalysis


class ClauseAnalysisRepository:
    @staticmethod
    def save_clause_analyses(
        db: Session,
        document_id: str,
        chunk_id: str,
        findings: list,
    ):
        records = []

        for finding in findings:
            record = ClauseAnalysis(
                document_id=document_id,
                chunk_id=chunk_id,
                clause_type=finding["clause_type"],
                matched_text=finding["matched_text"],
                confidence_score=finding["confidence_score"],
                analysis_metadata=finding["metadata"],
            )

            db.add(record)
            records.append(record)

        # Flush assigns DB-generated IDs without committing transaction
        db.flush()

        return records