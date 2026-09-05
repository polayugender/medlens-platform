import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.core.provenance import SourceProvenance

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, default=1, nullable=False)
    summary_text = Column(Text, nullable=False)
    
    based_on_report_ids = Column(JSON, default=list) # ["report-uuid-1", "report-uuid-2"]
    based_on_intake_version = Column(Integer, nullable=True)
    
    source = Column(String(32), default=SourceProvenance.AI_GENERATED.value, nullable=False)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    patient = relationship("Patient", back_populates="summaries")
