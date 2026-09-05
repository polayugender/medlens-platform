from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.patient import Patient
from app.models.extracted_test import ExtractedTest
from app.schemas.extracted_test import (
    ExtractedTestResponse,
    ExtractedTestUpdate,
    VerifyTestsBatchRequest
)
from app.core.flag_calculator import parse_reference_range, compute_flag
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="", tags=["Extraction & Verification"])

@router.get("/patients/{patient_id}/tests", response_model=List[ExtractedTestResponse])
async def list_patient_tests(
    patient_id: str,
    verified: Optional[bool] = Query(None, description="Filter by verification status"),
    report_id: Optional[str] = Query(None, description="Filter by report ID"),
    db: AsyncSession = Depends(get_db)
):
    query = select(ExtractedTest).where(ExtractedTest.patient_id == patient_id)
    if verified is not None:
        query = query.where(ExtractedTest.verified == verified)
    if report_id:
        query = query.where(ExtractedTest.report_id == report_id)

    query = query.order_by(ExtractedTest.created_at.asc())
    result = await db.execute(query)
    tests = result.scalars().all()
    return tests

@router.put("/tests/{test_id}", response_model=ExtractedTestResponse)
async def update_extracted_test(
    test_id: str,
    payload: ExtractedTestUpdate,
    actor: str = Query("User", description="Identity of person editing"),
    db: AsyncSession = Depends(get_db)
):
    test = await db.get(ExtractedTest, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    before_state = {
        "test_name": test.test_name,
        "value": test.value,
        "unit": test.unit,
        "reference_range_raw": test.reference_range_raw,
        "flag": test.flag,
        "verified": test.verified
    }

    if payload.test_name is not None:
        test.test_name = payload.test_name
    if payload.value is not None:
        test.value = payload.value
        # Re-parse numeric if not supplied
        if payload.value_numeric is not None:
            test.value_numeric = payload.value_numeric
        else:
            try:
                test.value_numeric = float(payload.value)
            except ValueError:
                test.value_numeric = None
    elif payload.value_numeric is not None:
        test.value_numeric = payload.value_numeric

    if payload.unit is not None:
        test.unit = payload.unit

    if payload.reference_range_raw is not None:
        test.reference_range_raw = payload.reference_range_raw
        low_bound, high_bound = parse_reference_range(payload.reference_range_raw)
        test.reference_range_low = low_bound
        test.reference_range_high = high_bound

    if payload.verified is not None:
        test.verified = payload.verified
        if payload.verified:
            test.verified_by = actor
            test.verified_at = datetime.now(timezone.utc)

    # Deterministically re-compute flag with source range
    test.flag = compute_flag(
        value_numeric=test.value_numeric,
        low=test.reference_range_low,
        high=test.reference_range_high,
        qualitative_value=test.value
    ).value

    await db.commit()
    await db.refresh(test)

    await log_audit_event(
        db=db,
        patient_id=test.patient_id,
        actor=actor,
        action="TEST_EDITED",
        entity="ExtractedTest",
        entity_id=test.id,
        before_state=before_state,
        after_state={
            "test_name": test.test_name,
            "value": test.value,
            "unit": test.unit,
            "reference_range_raw": test.reference_range_raw,
            "flag": test.flag,
            "verified": test.verified
        }
    )

    return test

@router.post("/patients/{patient_id}/tests/verify-batch", response_model=List[ExtractedTestResponse])
async def verify_tests_batch(
    patient_id: str,
    payload: VerifyTestsBatchRequest,
    db: AsyncSession = Depends(get_db)
):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    updated_tests: List[ExtractedTest] = []
    now = datetime.now(timezone.utc)

    for item in payload.tests:
        test = await db.get(ExtractedTest, item.id)
        if not test or test.patient_id != patient_id:
            continue

        before_state = {
            "test_name": test.test_name,
            "value": test.value,
            "verified": test.verified
        }

        # Apply any human adjustments made on the review screen
        test.test_name = item.test_name
        test.value = item.value
        test.unit = item.unit
        test.reference_range_raw = item.reference_range_raw
        
        # Parse bounds
        low_bound, high_bound = parse_reference_range(item.reference_range_raw)
        test.reference_range_low = low_bound
        test.reference_range_high = high_bound
        
        if item.value_numeric is not None:
            test.value_numeric = item.value_numeric
        else:
            try:
                test.value_numeric = float(item.value)
            except ValueError:
                test.value_numeric = None

        # Re-compute flag deterministically
        test.flag = compute_flag(
            value_numeric=test.value_numeric,
            low=low_bound,
            high=high_bound,
            qualitative_value=test.value
        ).value

        # Mark verified
        test.verified = True
        test.verified_by = payload.verified_by
        test.verified_at = now

        updated_tests.append(test)

    await db.commit()

    # Log verification batch
    await log_audit_event(
        db=db,
        patient_id=patient_id,
        actor=payload.verified_by,
        action="TESTS_BATCH_VERIFIED",
        entity="ExtractedTest",
        entity_id=patient_id,
        after_state={
            "verified_count": len(updated_tests),
            "test_ids": [t.id for t in updated_tests]
        }
    )

    for t in updated_tests:
        await db.refresh(t)

    return updated_tests

@router.delete("/tests/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_extracted_test(test_id: str, db: AsyncSession = Depends(get_db)):
    test = await db.get(ExtractedTest, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    p_id = test.patient_id
    tname = test.test_name
    await db.delete(test)
    await db.commit()

    await log_audit_event(
        db=db,
        patient_id=p_id,
        actor="User",
        action="TEST_DELETED",
        entity="ExtractedTest",
        entity_id=test_id,
        before_state={"test_name": tname}
    )
    return None
