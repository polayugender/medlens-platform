from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.models.patient import Patient
from app.models.report import MedicalReport
from app.models.extracted_test import ExtractedTest
from app.models.summary import Summary
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("", response_model=List[PatientResponse])
async def list_patients(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).order_by(Patient.created_at.desc()))
    patients = result.scalars().all()
    return patients

from typing import List, Optional

@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    payload: PatientCreate,
    actor: Optional[str] = "User",
    db: AsyncSession = Depends(get_db)
):
    patient = Patient(
        name=payload.name,
        dob=payload.dob,
        sex=payload.sex,
        phone=payload.phone,
        abha_id=payload.abha_id,
        state=payload.state,
        city=payload.city,
        emergency_contact=payload.emergency_contact
    )
    db.add(patient)
    await db.commit()
    await db.refresh(patient)

    await log_audit_event(
        db=db,
        patient_id=patient.id,
        actor=actor or "User",
        action="PATIENT_CREATED",
        entity="Patient",
        entity_id=patient.id,
        after_state={
            "name": patient.name,
            "dob": str(patient.dob),
            "sex": patient.sex,
            "phone": patient.phone,
            "abha_id": patient.abha_id,
            "state": patient.state,
            "city": patient.city
        }
    )

    return patient

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: str, db: AsyncSession = Depends(get_db)):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    payload: PatientUpdate,
    actor: Optional[str] = "User",
    db: AsyncSession = Depends(get_db)
):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    before_state = {
        "name": patient.name,
        "dob": str(patient.dob),
        "sex": patient.sex,
        "phone": patient.phone,
        "abha_id": patient.abha_id,
        "state": patient.state,
        "city": patient.city
    }
    if payload.name is not None:
        patient.name = payload.name
    if payload.dob is not None:
        patient.dob = payload.dob
    if payload.sex is not None:
        patient.sex = payload.sex
    if payload.phone is not None:
        patient.phone = payload.phone
    if payload.abha_id is not None:
        patient.abha_id = payload.abha_id
    if payload.state is not None:
        patient.state = payload.state
    if payload.city is not None:
        patient.city = payload.city
    if payload.emergency_contact is not None:
        patient.emergency_contact = payload.emergency_contact

    await db.commit()
    await db.refresh(patient)

    await log_audit_event(
        db=db,
        patient_id=patient.id,
        actor=actor or "User",
        action="PATIENT_UPDATED",
        entity="Patient",
        entity_id=patient.id,
        before_state=before_state,
        after_state={"name": patient.name, "dob": str(patient.dob), "sex": patient.sex}
    )

    return patient

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(patient_id: str, db: AsyncSession = Depends(get_db)):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    await db.delete(patient)
    await db.commit()
    return None
