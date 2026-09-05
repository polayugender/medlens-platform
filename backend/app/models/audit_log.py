import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    actor = Column(String(128), default="User", nullable=False)
    action = Column(String(64), nullable=False) # e.g. INTAKE_CREATED, REPORT_UPLOADED, TEST_VERIFIED, TEST_EDITED, SUMMARY_GENERATED
    entity = Column(String(64), nullable=False) # Patient, IntakeRecord, MedicalReport, ExtractedTest, Summary
    entity_id = Column(String(36), nullable=False)
    
    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    patient = relationship("Patient", back_populates="audit_logs")
