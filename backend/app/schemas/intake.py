from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class MedicationItem(BaseModel):
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None

class IntakeCreate(BaseModel):
    age: int = Field(..., ge=0, le=130)
    sex: str
    symptoms: List[str] = Field(default_factory=list)
    existing_conditions: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    medications: List[MedicationItem] = Field(default_factory=list)

class IntakeResponse(BaseModel):
    id: str
    patient_id: str
    version: int
    age: int
    sex: str
    symptoms: List[str]
    existing_conditions: List[str]
    allergies: List[str]
    medications: List[Dict[str, Any]]
    source: str
    created_at: datetime

    class Config:
        from_attributes = True
