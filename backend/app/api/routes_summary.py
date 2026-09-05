from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.patient import Patient
from app.models.intake import IntakeRecord
from app.models.report import MedicalReport
from app.models.extracted_test import ExtractedTest
from app.models.summary import Summary
from app.schemas.summary import SummaryResponse, SummaryGenerateRequest
from app.services.summarizer import generate_patient_summary
from app.services.audit_service import log_audit_event
from app.core.provenance import SourceProvenance

router = APIRouter(prefix="/patients/{patient_id}/summary", tags=["Summary"])

@router.get("", response_model=Optional[SummaryResponse])
async def get_patient_summary(patient_id: str, db: AsyncSession = Depends(get_db)):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    result = await db.execute(
        select(Summary)
        .where(Summary.patient_id == patient_id)
        .order_by(Summary.version.desc())
    )
    summary = result.scalars().first()
    return summary

@router.post("", response_model=SummaryResponse, status_code=status.HTTP_201_CREATED)
async def create_or_regenerate_summary(
    patient_id: str,
    payload: SummaryGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Fetch latest intake
    intake_res = await db.execute(
        select(IntakeRecord)
        .where(IntakeRecord.patient_id == patient_id)
        .order_by(IntakeRecord.version.desc())
    )
    latest_intake = intake_res.scalars().first()

    # Fetch all verified tests
    tests_res = await db.execute(
        select(ExtractedTest)
        .where(ExtractedTest.patient_id == patient_id)
        .where(ExtractedTest.verified == True)
        .order_by(ExtractedTest.created_at.asc())
    )
    verified_tests = tests_res.scalars().all()

    # Fetch linked reports
    report_ids = list(set([t.report_id for t in verified_tests]))

    # Prepare data payload for summarizer
    patient_dict = {
        "name": patient.name,
        "dob": str(patient.dob),
        "sex": patient.sex
    }
    intake_dict = None
    if latest_intake:
        intake_dict = {
            "version": latest_intake.version,
            "age": latest_intake.age,
            "sex": latest_intake.sex,
            "symptoms": latest_intake.symptoms,
            "existing_conditions": latest_intake.existing_conditions,
            "allergies": latest_intake.allergies,
            "medications": latest_intake.medications
        }

    tests_list = [
        {
            "test_name": t.test_name,
            "value": t.value,
            "unit": t.unit,
            "reference_range_raw": t.reference_range_raw,
            "flag": t.flag
        }
        for t in verified_tests
    ]

    # Generate summary adhering strictly to non-diagnostic prompt
    generated_text = await generate_patient_summary(
        patient_data=patient_dict,
        intake_data=intake_dict,
        verified_tests=tests_list
    )

    # Determine version
    curr_v_res = await db.execute(
        select(Summary.version)
        .where(Summary.patient_id == patient_id)
        .order_by(Summary.version.desc())
    )
    highest_v = curr_v_res.scalars().first() or 0
    new_v = highest_v + 1

    summary = Summary(
        patient_id=patient_id,
        version=new_v,
        summary_text=generated_text,
        based_on_report_ids=report_ids,
        based_on_intake_version=latest_intake.version if latest_intake else None,
        source=SourceProvenance.AI_GENERATED.value
    )
    db.add(summary)
    await db.commit()
    await db.refresh(summary)

    await log_audit_event(
        db=db,
        patient_id=patient_id,
        actor="AI Engine",
        action="SUMMARY_GENERATED",
        entity="Summary",
        entity_id=summary.id,
        after_state={
            "version": new_v,
            "based_on_reports_count": len(report_ids),
            "based_on_intake_version": latest_intake.version if latest_intake else None
        }
    )

    return summary
