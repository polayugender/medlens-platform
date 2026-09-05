from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel

class PatientBase(BaseModel):
    name: str
    dob: date
    sex: str
    phone: Optional[str] = None
    abha_id: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    emergency_contact: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    dob: Optional[date] = None
    sex: Optional[str] = None
    phone: Optional[str] = None
    abha_id: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    emergency_contact: Optional[str] = None

class PatientResponse(PatientBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
