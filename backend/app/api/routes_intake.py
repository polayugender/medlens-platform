from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.patient import Patient
from app.models.intake import IntakeRecord
from app.schemas.intake import IntakeCreate, IntakeResponse
from app.services.audit_service import log_audit_event
from app.core.provenance import SourceProvenance

router = APIRouter(prefix="/patients/{patient_id}/intake", tags=["Intake"])

@router.get("", response_model=Optional[IntakeResponse])
async def get_latest_intake(patient_id: str, db: AsyncSession = Depends(get_db)):
    # Check patient exists
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    result = await db.execute(
        select(IntakeRecord)
        .where(IntakeRecord.patient_id == patient_id)
        .order_by(IntakeRecord.version.desc())
    )
    return result.scalars().first()

@router.get("/history", response_model=List[IntakeResponse])
async def get_intake_history(patient_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(IntakeRecord)
        .where(IntakeRecord.patient_id == patient_id)
        .order_by(IntakeRecord.version.desc())
    )
    return result.scalars().all()

@router.post("", response_model=IntakeResponse, status_code=status.HTTP_201_CREATED)
async def create_intake_record(
    patient_id: str,
    payload: IntakeCreate,
    actor: Optional[str] = "User",
    db: AsyncSession = Depends(get_db)
):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Find highest current version
    result = await db.execute(
        select(IntakeRecord.version)
        .where(IntakeRecord.patient_id == patient_id)
        .order_by(IntakeRecord.version.desc())
    )
    highest_v = result.scalars().first() or 0
    new_version = highest_v + 1

    # Convert medication items to dicts
    meds_data = [m.model_dump() for m in payload.medications]

    record = IntakeRecord(
        patient_id=patient_id,
        version=new_version,
        age=payload.age,
        sex=payload.sex,
        symptoms=payload.symptoms,
        existing_conditions=payload.existing_conditions,
        allergies=payload.allergies,
        medications=meds_data,
        source=SourceProvenance.USER_INPUT.value
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    action_name = "INTAKE_CREATED" if actor == "patient_self_service" else "INTAKE_SUBMITTED"
    await log_audit_event(
        db=db,
        patient_id=patient_id,
        actor=actor or "User",
        action=action_name,
        entity="IntakeRecord",
        entity_id=record.id,
        after_state={
            "version": new_version,
            "symptoms_count": len(payload.symptoms),
            "medications_count": len(payload.medications),
            "allergies_count": len(payload.allergies)
        }
    )

    return record
