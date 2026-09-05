import shutil
import uuid
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.config import settings
from app.models.patient import Patient
from app.models.report import MedicalReport
from app.models.extracted_test import ExtractedTest
from app.schemas.report import MedicalReportResponse
from app.schemas.extracted_test import ExtractedTestResponse
from app.services.pdf_parser import parse_pdf_document, find_snippet_in_text
from app.services.ai_extractor import extract_structured_tests_from_report
from app.core.flag_calculator import parse_reference_range, parse_reference_range_with_provenance, compute_flag
from app.core.provenance import SourceProvenance, FlagCategory
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="", tags=["Reports"])

@router.get("/patients/{patient_id}/reports", response_model=List[MedicalReportResponse])
async def list_patient_reports(patient_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MedicalReport)
        .where(MedicalReport.patient_id == patient_id)
        .order_by(MedicalReport.uploaded_at.desc())
    )
    reports = result.scalars().all()
    return reports

@router.post("/patients/{patient_id}/reports", response_model=MedicalReportResponse)
async def upload_medical_report(
    patient_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Verify patient exists
    p_check = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = p_check.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Ensure storage directory exists
    storage_dir = Path("backend/storage/reports")
    storage_dir.mkdir(parents=True, exist_ok=True)

    file_extension = Path(file.filename or "report.pdf").suffix.lower()
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = storage_dir / unique_filename

    # Read and persist file
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    # Extract text and metadata
    raw_text = ""
    page_count = 1
    if file_extension == ".pdf":
        raw_text, page_count = parse_pdf_document(file_path)
    else:
        try:
            raw_text = contents.decode("utf-8", errors="ignore")
        except Exception:
            raw_text = "Binary report data"

    # Extract clinical lab tests via zero-hallucination extraction engine
    extraction_result = await extract_structured_tests_from_report(raw_text)

    # Persist report entity
    report = MedicalReport(
        patient_id=patient_id,
        original_filename=file.filename or "unknown.pdf",
        file_url=f"/storage/reports/{unique_filename}",
        file_type=file_extension.replace(".", "") or "pdf",
        report_date=extraction_result.report_metadata.report_date,
        report_type=extraction_result.report_metadata.report_type or "Laboratory Report",
        facility_name=extraction_result.report_metadata.facility_name,
        raw_text=raw_text,
        page_count=page_count
    )
    db.add(report)
    await db.flush()

    # Save extracted tests with human-in-the-loop pending verification
    created_tests_count = 0
    for test_item in extraction_result.extracted_tests:
        # Compute range bounds purely from source text with zero hallucination
        low_bound, high_bound, source_provided = parse_reference_range_with_provenance(test_item.reference_range_raw)
        
        # Deterministically compute flag
        computed_flag = compute_flag(
            value_numeric=test_item.value_numeric,
            low=low_bound,
            high=high_bound,
            qualitative_value=test_item.value,
            source_provided=source_provided,
            operator=test_item.operator
        )

        test_record = ExtractedTest(
            report_id=report.id,
            patient_id=patient_id,
            test_name=test_item.test_name,
            value=test_item.value,
            value_numeric=test_item.value_numeric,
            unit=test_item.unit,
            reference_range_raw=test_item.reference_range_raw,
            reference_range_low=low_bound,
            reference_range_high=high_bound,
            flag=computed_flag.value,
            source=SourceProvenance.AI_EXTRACTED.value,
            verified=False,  # Needs human confirmation
            raw_snippet=test_item.raw_snippet,
            confidence_score=test_item.confidence,
            location_meta={"page": 1}
        )
        db.add(test_record)
        created_tests_count += 1

    await db.commit()
    await db.refresh(report)

    # Log audit event
    await log_audit_event(
        db=db,
        patient_id=patient_id,
        actor="AI Pipeline",
        action="REPORT_UPLOADED_AND_PARSED",
        entity="MedicalReport",
        entity_id=report.id,
        after_state={
            "filename": filename,
            "extracted_tests_count": created_tests_count,
            "report_type": report.report_type
        }
    )

    resp = MedicalReportResponse.model_validate(report)
    resp.test_count = created_tests_count
    return resp

@router.get("/reports/{report_id}")
async def get_report_details(report_id: str, db: AsyncSession = Depends(get_db)):
    report = await db.get(MedicalReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    result = await db.execute(
        select(ExtractedTest)
        .where(ExtractedTest.report_id == report_id)
        .order_by(ExtractedTest.created_at.asc())
    )
    tests = result.scalars().all()

    # Locate preview images
    report_stem = Path(report.file_url).stem
    previews = []
    for p in range(1, report.page_count + 1):
        prev_path = settings.PREVIEWS_DIR / f"{report_stem}_p{p}.png"
        if prev_path.exists():
            previews.append(f"/storage/previews/{report_stem}_p{p}.png")

    return {
        "report": MedicalReportResponse.model_validate(report),
        "tests": [ExtractedTestResponse.model_validate(t) for t in tests],
        "previews": previews
    }

@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(report_id: str, db: AsyncSession = Depends(get_db)):
    report = await db.get(MedicalReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    p_id = report.patient_id
    fname = report.original_filename
    await db.delete(report)
    await db.commit()

    await log_audit_event(
        db=db,
        patient_id=p_id,
        actor="User",
        action="REPORT_DELETED",
        entity="MedicalReport",
        entity_id=report_id,
        before_state={"filename": fname}
    )
    return None
