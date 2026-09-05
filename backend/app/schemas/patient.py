from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel

class PatientBase(BaseModel):
    name: str
    dob: date
    sex: str

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    dob: Optional[date] = None
    sex: Optional[str] = None

class PatientResponse(PatientBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
