from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ExtractedTestBase(BaseModel):
    test_name: str
    value: str
    value_numeric: Optional[float] = None
    unit: Optional[str] = None
    reference_range_raw: Optional[str] = None
    reference_range_low: Optional[float] = None
    reference_range_high: Optional[float] = None

class ExtractedTestUpdate(BaseModel):
    test_name: Optional[str] = None
    value: Optional[str] = None
    value_numeric: Optional[float] = None
    unit: Optional[str] = None
    reference_range_raw: Optional[str] = None
    reference_range_low: Optional[float] = None
    reference_range_high: Optional[float] = None
    verified: Optional[bool] = None

class ExtractedTestResponse(ExtractedTestBase):
    id: str
    report_id: str
    patient_id: str
    flag: str
    source: str
    verified: bool
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    raw_snippet: Optional[str] = None
    confidence_score: float
    location_meta: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class VerifyBatchItem(BaseModel):
    id: str
    test_name: str
    value: str
    value_numeric: Optional[float] = None
    unit: Optional[str] = None
    reference_range_raw: Optional[str] = None
    reference_range_low: Optional[float] = None
    reference_range_high: Optional[float] = None

class VerifyTestsBatchRequest(BaseModel):
    verified_by: str = "User"
    tests: List[VerifyBatchItem]
