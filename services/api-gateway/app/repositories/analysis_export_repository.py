from sqlalchemy.orm import Session

from app.db.models.clause_analysis import (
    ClauseAnalysis,
)


class AnalysisExportRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def list_analyses(
        self,
        owner_id: str,
        tenant_id: str,
    ):
        return (
            self.db.query(
                ClauseAnalysis
            )
            .filter(
                ClauseAnalysis.owner_id
                == owner_id,
                ClauseAnalysis.tenant_id
                == tenant_id,
            )
            .all()
        )