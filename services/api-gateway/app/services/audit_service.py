from typing import Any

from sqlalchemy.orm import Session

from app.db.models.audit_log import AuditLog


class AuditService:

    @staticmethod
    def log_event(
        db: Session,
        *,
        tenant_id: str,
        event_type: str,
        action: str,
        status: str = "success",
        user_id: str | None = None,
        api_key_id: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        event_metadata: dict[str, Any] | None = None,
    ) -> AuditLog:

        audit_log = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            api_key_id=api_key_id,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            event_metadata=event_metadata,
        )

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        return audit_log