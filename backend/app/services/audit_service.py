from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog

async def log_audit_event(
    db: AsyncSession,
    patient_id: str,
    action: str,
    entity: str,
    entity_id: str,
    actor: str = "User",
    before_state: Optional[Dict[str, Any]] = None,
    after_state: Optional[Dict[str, Any]] = None,
) -> AuditLog:
    """
    Appends an immutable audit log entry for traceability and HIPAA-style governance.
    """
    log_entry = AuditLog(
        patient_id=patient_id,
        actor=actor,
        action=action,
        entity=entity,
        entity_id=entity_id,
        before_state=before_state,
        after_state=after_state,
    )
    db.add(log_entry)
    await db.commit()
    await db.refresh(log_entry)
    return log_entry
