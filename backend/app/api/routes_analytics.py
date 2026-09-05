from collections import defaultdict
from datetime import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.patient import Patient
from app.models.intake import IntakeRecord
from app.models.report import MedicalReport
from app.models.extracted_test import ExtractedTest
from app.models.summary import Summary
from app.models.audit_log import AuditLog
from app.services.conflict_detector import detect_clinical_inconsistencies

router = APIRouter(prefix="/patients/{patient_id}", tags=["Analytics & Export"])

@router.get("/conflicts")
async def get_patient_conflicts(patient_id: str, db: AsyncSession = Depends(get_db)):
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

    intake_dict = None
    if latest_intake:
        intake_dict = {
            "allergies": latest_intake.allergies,
            "medications": latest_intake.medications,
            "existing_conditions": latest_intake.existing_conditions,
            "symptoms": latest_intake.symptoms
        }

    # Fetch reports
    rep_res = await db.execute(
        select(MedicalReport).where(MedicalReport.patient_id == patient_id)
    )
    reports = rep_res.scalars().all()
    reports_list = [{"id": r.id, "report_date": str(r.report_date)} for r in reports]

    # Fetch tests
    tests_res = await db.execute(
        select(ExtractedTest).where(ExtractedTest.patient_id == patient_id)
    )
    tests = tests_res.scalars().all()
    tests_list = [
        {
            "id": t.id,
            "test_name": t.test_name,
            "value": t.value,
            "flag": t.flag,
            "reference_range_raw": t.reference_range_raw,
            "verified": t.verified
        }
        for t in tests
    ]

    conflicts = detect_clinical_inconsistencies(
        intake_data=intake_dict,
        reports=reports_list,
        tests=tests_list
    )
    return {"conflicts": conflicts, "total": len(conflicts)}

@router.get("/trends")
async def get_test_trends(patient_id: str, db: AsyncSession = Depends(get_db)):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Join extracted tests with their parent medical report to get the report date
    result = await db.execute(
        select(ExtractedTest, MedicalReport.report_date, MedicalReport.original_filename)
        .join(MedicalReport, ExtractedTest.report_id == MedicalReport.id)
        .where(ExtractedTest.patient_id == patient_id)
        .where(ExtractedTest.value_numeric.isnot(None))
        .order_by(MedicalReport.report_date.asc(), ExtractedTest.created_at.asc())
    )
    rows = result.all()

    # Group by standardized test name
    trends_map = defaultdict(list)
    for test, rep_date, filename in rows:
        norm_name = test.test_name.strip()
        trends_map[norm_name].append({
            "test_id": test.id,
            "date": str(rep_date) if rep_date else str(test.created_at.date()),
            "value": test.value_numeric,
            "unit": test.unit,
            "reference_range_low": test.reference_range_low,
            "reference_range_high": test.reference_range_high,
            "flag": test.flag,
            "verified": test.verified,
            "report_name": filename
        })

    # Return grouped trends where test has at least 1 measurement
    response = []
    for test_name, points in trends_map.items():
        response.append({
            "test_name": test_name,
            "points_count": len(points),
            "unit": points[0]["unit"] if points else None,
            "points": points
        })

    # Sort tests with multiple readings first
    response.sort(key=lambda x: x["points_count"], reverse=True)
    return response

@router.get("/export")
async def export_full_patient_record(
    patient_id: str,
    format: str = "json",
    db: AsyncSession = Depends(get_db)
):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Latest intake
    intake_res = await db.execute(
        select(IntakeRecord).where(IntakeRecord.patient_id == patient_id).order_by(IntakeRecord.version.desc())
    )
    latest_intake = intake_res.scalars().first()

    # Reports
    rep_res = await db.execute(
        select(MedicalReport).where(MedicalReport.patient_id == patient_id).order_by(MedicalReport.report_date.desc())
    )
    reports = rep_res.scalars().all()

    # Verified tests
    test_res = await db.execute(
        select(ExtractedTest).where(ExtractedTest.patient_id == patient_id).order_by(ExtractedTest.created_at.asc())
    )
    tests = test_res.scalars().all()
    verified_tests = [t for t in tests if t.verified]

    # Summary
    sum_res = await db.execute(
        select(Summary).where(Summary.patient_id == patient_id).order_by(Summary.version.desc())
    )
    summary = sum_res.scalars().first()

    # Audit logs
    audit_res = await db.execute(
        select(AuditLog).where(AuditLog.patient_id == patient_id).order_by(AuditLog.timestamp.desc())
    )
    audit_logs = audit_res.scalars().all()

    patient_dict = {
        "id": patient.id,
        "name": patient.name,
        "dob": str(patient.dob),
        "sex": patient.sex,
    }

    intake_dict = {
        "version": latest_intake.version,
        "age": latest_intake.age,
        "sex": latest_intake.sex,
        "symptoms": latest_intake.symptoms or [],
        "existing_conditions": latest_intake.existing_conditions or [],
        "allergies": latest_intake.allergies or [],
        "medications": latest_intake.medications or []
    } if latest_intake else None

    tests_list = [
        {
            "id": t.id,
            "test_name": t.test_name,
            "value": t.value,
            "value_numeric": t.value_numeric,
            "unit": t.unit,
            "reference_range_raw": t.reference_range_raw,
            "flag": t.flag,
            "source": t.source,
            "verified": t.verified,
            "verified_by": t.verified_by,
            "verified_at": str(t.verified_at) if t.verified_at else None,
            "raw_snippet": t.raw_snippet
        }
        for t in (verified_tests if format == "pdf" else tests)
    ]

    summary_dict = {
        "version": summary.version,
        "summary_text": summary.summary_text,
        "source": summary.source,
        "generated_at": str(summary.generated_at),
        "disclaimer": "This is an organizational summary, not a medical diagnosis. Consult a healthcare professional."
    } if summary else None

    audit_list = [
        {
            "id": a.id,
            "actor": a.actor,
            "action": a.action,
            "entity": a.entity,
            "timestamp": str(a.timestamp)
        }
        for a in audit_logs
    ]

    # Handle PDF export format
    if format.lower() == "pdf":
        from app.services.pdf_exporter import generate_patient_clinical_pdf
        from fastapi.responses import Response

        pdf_bytes = generate_patient_clinical_pdf(
            patient=patient_dict,
            intake=intake_dict,
            verified_tests=tests_list,
            summary=summary_dict,
            audit_logs=audit_list
        )

        safe_name = patient.name.replace(" ", "_")
        filename = f"MedLens_{safe_name}_Clinical_Record.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/pdf"
            }
        )

    # Return JSON export format
    return {
        "metadata": {
            "exported_at": str(datetime.now()),
            "system": "MedLens AI-Powered Clinical Intelligence",
            "safety_disclaimer": "This is an organizational summary, not a medical diagnosis. Consult a healthcare professional."
        },
        "patient": patient_dict,
        "intake": intake_dict,
        "reports": [
            {
                "id": r.id,
                "filename": r.original_filename,
                "date": str(r.report_date),
                "type": r.report_type,
                "facility": r.facility_name
            }
            for r in reports
        ],
        "structured_tests": tests_list,
        "verified_tests": [t for t in tests_list if t.get("verified")],
        "summary": summary_dict,
        "audit_logs": audit_list,
        "disclaimer": "This is an organizational summary, not a medical diagnosis. Consult a healthcare professional."
    }
