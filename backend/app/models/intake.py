import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.core.provenance import SourceProvenance

def generate_uuid() -> str:
    return str(uuid.uuid4())

class IntakeRecord(Base):
    __tablename__ = "intake_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, default=1, nullable=False)
    age = Column(Integer, nullable=False)
    sex = Column(String(32), nullable=False)
    
    # Clinical structured arrays
    symptoms = Column(JSON, default=list)            # ["fatigue", "dizziness"]
    existing_conditions = Column(JSON, default=list) # ["Hypertension", "Type 2 Diabetes"]
    allergies = Column(JSON, default=list)           # ["Penicillin", "Sulfa drugs"]
    medications = Column(JSON, default=list)         # [{"name": "Metformin", "dosage": "500mg", "frequency": "Daily", "route": "Oral"}]
    
    # Provenance
    source = Column(String(32), default=SourceProvenance.USER_INPUT.value, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    patient = relationship("Patient", back_populates="intake_records")
