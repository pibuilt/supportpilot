from fastapi import (
    APIRouter,
    Depends,
    Query,
    Request,
)
from fastapi.responses import (
    Response,
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.repositories.document_repository import (
    DocumentRepository,
)

from app.services.export_service import (
    ExportService,
)

from app.repositories.chat_export_repository import (
    ChatExportRepository,
)

from app.repositories.analysis_export_repository import (
    AnalysisExportRepository,
)


router = APIRouter(
    prefix="/v1/export",
    tags=["Exports"],
)


@router.get("/documents")
def export_documents(
    request: Request,
    format: str = Query(
        "json",
        pattern="^(json|csv)$",
    ),
    db: Session = Depends(get_db),
):

    owner_id = (
        request.state.owner
    )

    tenant_id = (
        request.state.tenant_id
    )

    repo = DocumentRepository(
        db
    )

    documents = (
        repo.list_documents(
            owner_id=owner_id,
            tenant_id=tenant_id,
        )
    )

    rows = [
        {
            "document_id": (
                row.document_id
            ),
            "chunk_count": (
                row.chunk_count
            ),
            "embedding_model": (
                row.embedding_model
            ),
            "embedding_version": (
                row.embedding_version
            ),
        }
        for row in documents
    ]

    if format == "csv":

        content = (
            ExportService.to_csv(
                rows
            )
        )

        return Response(
            content=content,
            media_type="text/csv",
            headers={
                "Content-Disposition":
                "attachment; filename=documents.csv"
            },
        )

    content = (
        ExportService.to_json(
            rows
        )
    )

    return Response(
        content=content,
        media_type="application/json",
        headers={
            "Content-Disposition":
            "attachment; filename=documents.json"
        },
    )


@router.get("/sessions")
def export_sessions(
    request: Request,
    format: str = Query(
        "json",
        pattern="^(json|csv)$",
    ),
    db: Session = Depends(get_db),
):
    owner_id = (
        request.state.owner
    )

    tenant_id = (
        request.state.tenant_id
    )

    repo = ChatExportRepository(
        db
    )

    sessions = (
        repo.list_sessions(
            owner_id=owner_id,
            tenant_id=tenant_id,
        )
    )

    rows = []

    for session in sessions:

        messages = (
            repo.get_messages(
                session.id
            )
        )

        rows.append(
            {
                "session_id": session.id,
                "title": session.title,
                "message_count": (
                    session.message_count
                ),
                "messages": [
                    {
                        "role": m.role,
                        "content": m.content,
                    }
                    for m in messages
                ],
            }
        )

    if format == "csv":

        flat_rows = []

        for row in rows:

            for message in row[
                "messages"
            ]:

                flat_rows.append(
                    {
                        "session_id":
                        row[
                            "session_id"
                        ],

                        "role":
                        message[
                            "role"
                        ],

                        "content":
                        message[
                            "content"
                        ],
                    }
                )

        content = (
            ExportService.to_csv(
                flat_rows
            )
        )

        return Response(
            content=content,
            media_type="text/csv",
            headers={
                "Content-Disposition":
                "attachment; filename=sessions.csv"
            },
        )

    content = (
        ExportService.to_json(
            rows
        )
    )

    return Response(
        content=content,
        media_type="application/json",
        headers={
            "Content-Disposition":
            "attachment; filename=sessions.json"
        },
    )

@router.get("/analyses")
@router.get("/analyses")
def export_analyses(
    request: Request,
    format: str = Query(
        "json",
        pattern="^(json|csv)$",
    ),
    db: Session = Depends(get_db),
):
    owner_id = (
        request.state.owner
    )

    tenant_id = (
        request.state.tenant_id
    )

    repo = (
        AnalysisExportRepository(
            db
        )
    )

    analyses = (
        repo.list_analyses(
            owner_id=owner_id,
            tenant_id=tenant_id,
        )
    )

    rows = [
        {
            "id": analysis.id,
            "document_id": (
                analysis.document_id
            ),
            "chunk_id": (
                analysis.chunk_id
            ),
            "clause_type": (
                analysis.clause_type
            ),
            "matched_text": (
                analysis.matched_text
            ),
            "confidence_score": (
                analysis.confidence_score
            ),
            "metadata": (
                analysis.analysis_metadata
            ),
            "schema_version": (
                analysis.schema_version
            ),
            "created_at": (
                analysis.created_at.isoformat()
                if analysis.created_at
                else None
            ),
        }
        for analysis in analyses
    ]

    if format == "csv":

        csv_rows = [
            {
                "id": row["id"],
                "document_id": row["document_id"],
                "chunk_id": row["chunk_id"],
                "clause_type": row["clause_type"],
                "matched_text": row["matched_text"],
                "confidence_score": row["confidence_score"],
                "schema_version": row["schema_version"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]

        content = (
            ExportService.to_csv(
                csv_rows
            )
        )

        return Response(
            content=content,
            media_type="text/csv",
            headers={
                "Content-Disposition":
                "attachment; filename=analyses.csv"
            },
        )

    content = (
        ExportService.to_json(
            rows
        )
    )

    return Response(
        content=content,
        media_type="application/json",
        headers={
            "Content-Disposition":
            "attachment; filename=analyses.json"
        },
    )