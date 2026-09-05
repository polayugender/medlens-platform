from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.patient import Patient
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogResponse

router = APIRouter(prefix="/patients/{patient_id}/audit-logs", tags=["Audit Trail"])

@router.get("", response_model=List[AuditLogResponse])
async def get_patient_audit_trail(patient_id: str, db: AsyncSession = Depends(get_db)):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.patient_id == patient_id)
        .order_by(AuditLog.timestamp.desc())
    )
    logs = result.scalars().all()
    return logs
