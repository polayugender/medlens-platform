from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class SummaryResponse(BaseModel):
    id: str
    patient_id: str
    version: int
    summary_text: str
    based_on_report_ids: List[str]
    based_on_intake_version: Optional[int] = None
    source: str
    generated_at: datetime
    disclaimer: str = "This is an organizational summary, not a medical diagnosis. Consult a healthcare professional."

    class Config:
        from_attributes = True

class SummaryGenerateRequest(BaseModel):
    patient_id: str
    regenerate: bool = False
