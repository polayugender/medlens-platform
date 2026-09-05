import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Date, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Patient(Base):
    __tablename__ = "patients"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    dob = Column(Date, nullable=False)
    sex = Column(String(32), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    intake_records = relationship("IntakeRecord", back_populates="patient", cascade="all, delete-orphan", order_by="desc(IntakeRecord.version)")
    reports = relationship("MedicalReport", back_populates="patient", cascade="all, delete-orphan", order_by="desc(MedicalReport.uploaded_at)")
    extracted_tests = relationship("ExtractedTest", back_populates="patient", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="patient", cascade="all, delete-orphan", order_by="desc(Summary.version)")
    audit_logs = relationship("AuditLog", back_populates="patient", cascade="all, delete-orphan", order_by="desc(AuditLog.timestamp)")
