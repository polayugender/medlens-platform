import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Index
from app.db.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    request_id = Column(String(36), unique=True, nullable=False, index=True, default=generate_uuid)
    phone = Column(String(32), nullable=False, index=True)
    hashed_otp = Column(String(255), nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    client_ip = Column(String(64), nullable=True)

    __table_args__ = (
        Index("ix_otp_phone_created", "phone", "created_at"),
    )

    def is_expired(self) -> bool:
        now = datetime.now(timezone.utc)
        exp = self.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        return now > exp

    def can_attempt(self) -> bool:
        return not self.is_verified and not self.is_expired() and self.attempts < self.max_attempts
