from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.embedding import Embedding


class DocumentRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def list_documents(
        self,
        owner_id: str,
        tenant_id: str,
    ):
        return (
            self.db.query(
                Embedding.document_id,
                func.count(
                    Embedding.id
                ).label(
                    "chunk_count"
                ),
                func.min(
                    Embedding.embedding_model
                ).label(
                    "embedding_model"
                ),
                func.min(
                    Embedding.embedding_version
                ).label(
                    "embedding_version"
                ),
            )
            .filter(
                Embedding.owner_id
                == owner_id,
                Embedding.tenant_id
                == tenant_id,
            )
            .group_by(
                Embedding.document_id
            )
            .all()
        )

    def get_document(
        self,
        owner_id: str,
        tenant_id: str,
        document_id: str,
    ):
        return (
            self.db.query(
                Embedding
            )
            .filter(
                Embedding.owner_id
                == owner_id,
                Embedding.tenant_id
                == tenant_id,
                Embedding.document_id
                == document_id,
            )
            .all()
        )

    def delete_document(
        self,
        owner_id: str,
        tenant_id: str,
        document_id: str,
    ):
        deleted = (
            self.db.query(
                Embedding
            )
            .filter(
                Embedding.owner_id
                == owner_id,
                Embedding.tenant_id
                == tenant_id,
                Embedding.document_id
                == document_id,
            )
            .delete(
                synchronize_session=False
            )
        )

        self.db.commit()

        return deleted