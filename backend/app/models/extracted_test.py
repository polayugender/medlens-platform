import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.core.provenance import SourceProvenance, FlagCategory

def generate_uuid() -> str:
    return str(uuid.uuid4())

class ExtractedTest(Base):
    __tablename__ = "extracted_tests"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_id = Column(String(36), ForeignKey("medical_reports.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    
    test_name = Column(String(255), nullable=False)
    value = Column(String(128), nullable=False)
    value_numeric = Column(Float, nullable=True)
    unit = Column(String(64), nullable=True)
    
    reference_range_raw = Column(String(128), nullable=True)
    reference_range_low = Column(Float, nullable=True)
    reference_range_high = Column(Float, nullable=True)
    
    flag = Column(String(32), default=FlagCategory.UNAVAILABLE.value, nullable=False)
    source = Column(String(32), default=SourceProvenance.AI_EXTRACTED.value, nullable=False)
    
    # Human-in-the-loop verification
    verified = Column(Boolean, default=False, nullable=False)
    verified_by = Column(String(128), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    # Traceability & provenance
    raw_snippet = Column(Text, nullable=True)
    confidence_score = Column(Float, default=1.0)
    location_meta = Column(JSON, default=dict) # {"page": 1, "line_index": 5}
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    report = relationship("MedicalReport", back_populates="extracted_tests")
    patient = relationship("Patient", back_populates="extracted_tests")
