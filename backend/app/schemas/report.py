from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel

class MedicalReportResponse(BaseModel):
    id: str
    patient_id: str
    original_filename: str
    file_url: str
    file_type: str
    report_date: Optional[date] = None
    report_type: Optional[str] = None
    facility_name: Optional[str] = None
    raw_text: Optional[str] = None
    page_count: int
    uploaded_at: datetime
    test_count: Optional[int] = 0

    class Config:
        from_attributes = True
