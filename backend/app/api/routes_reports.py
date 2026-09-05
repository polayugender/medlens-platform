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
from app.core.flag_calculator import parse_reference_range, compute_flag
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
    
    # Enrich with test counts
    responses = []
    for r in reports:
        count_res = await db.execute(
            select(func.count(ExtractedTest.id)).where(ExtractedTest.report_id == r.id)
        )
        test_count = count_res.scalar() or 0
        resp = MedicalReportResponse.model_validate(r)
        resp.test_count = test_count
        responses.append(resp)
    return responses

@router.post("/patients/{patient_id}/reports", response_model=MedicalReportResponse, status_code=status.HTTP_201_CREATED)
async def upload_medical_report(
    patient_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    filename = file.filename or "report.pdf"
    ext = Path(filename).suffix.lower()
    if ext not in [".pdf", ".png", ".jpg", ".jpeg"]:
        raise HTTPException(status_code=400, detail="Only PDF and image files (PNG/JPG) are supported")

    file_uuid = str(uuid.uuid4())
    stored_filename = f"{file_uuid}{ext}"
    stored_filepath = settings.REPORTS_DIR / stored_filename

    # Save to disk
    with open(stored_filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse document text
    raw_text = ""
    page_count = 1
    if ext == ".pdf":
        parsed_doc = parse_pdf_document(stored_filepath)
        raw_text = parsed_doc["raw_text"]
        page_count = parsed_doc["page_count"]
    else:
        raw_text = f"Scanned report image: {filename}"

    # Run AI extraction pipeline
    extraction_result = await extract_structured_tests_from_report(raw_text)

    parsed_date = None
    if extraction_result.report_metadata.report_date:
        try:
            # Normalize date
            date_str = extraction_result.report_metadata.report_date.replace("/", "-")
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            try:
                parsed_date = datetime.strptime(date_str, "%m-%d-%Y").date()
            except Exception:
                parsed_date = date.today()
    else:
        parsed_date = date.today()

    # Create MedicalReport record
    report = MedicalReport(
        id=file_uuid,
        patient_id=patient_id,
        original_filename=filename,
        file_url=f"/storage/reports/{stored_filename}",
        file_type="pdf" if ext == ".pdf" else "image",
        report_date=parsed_date,
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
        # Compute range bounds purely from source text
        low_bound, high_bound = parse_reference_range(test_item.reference_range_raw)
        
        # Deterministically compute flag
        computed_flag = compute_flag(
            value_numeric=test_item.value_numeric,
            low=low_bound,
            high=high_bound,
            qualitative_value=test_item.value
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
