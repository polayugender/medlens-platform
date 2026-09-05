import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_url = Column(String(512), nullable=False)
    file_type = Column(String(32), default="pdf") # pdf, image
    
    report_date = Column(Date, nullable=True)
    report_type = Column(String(128), nullable=True) # e.g. Comprehensive Metabolic Panel
    facility_name = Column(String(255), nullable=True)
    
    raw_text = Column(Text, nullable=True)
    page_count = Column(Integer, default=1)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    patient = relationship("Patient", back_populates="reports")
    extracted_tests = relationship("ExtractedTest", back_populates="report", cascade="all, delete-orphan")
