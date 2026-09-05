import re
from datetime import date, datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.patient import Patient
from app.models.audit_log import AuditLog
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_optional_authenticated_patient_id,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Full Legal Name")
    username: str = Field(..., min_length=3, max_length=20, description="Alphanumeric username (3-20 characters)")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Mobile number (+91 format)")
    password: str = Field(..., min_length=8, description="Password (min 8 characters, at least 1 uppercase, 1 digit)")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        clean = v.strip().lower()
        if not re.match(r"^[a-zA-Z0-9_-]{3,20}$", clean):
            raise ValueError("Username must be 3-20 characters and contain only letters, numbers, underscores, or hyphens.")
        return clean

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter (A-Z).")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number (0-9).")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if not v or not v.strip():
            return None
        clean = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", clean):
            raise ValueError("Please provide a valid email address.")
        return clean


class LoginRequest(BaseModel):
    username_or_email: str = Field(..., min_length=3, description="Username or registered Email")
    password: str = Field(..., min_length=1, description="Account password")
    remember_me: bool = False


class PatientAuthProfile(BaseModel):
    id: str
    name: str
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[str] = None
    sex: Optional[str] = None
    abha_id: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None


class AuthResponse(BaseModel):
    success: bool
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    patient: PatientAuthProfile


@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Registers a new patient account with Username, Password, and Full Name.
    Issues a signed JWT access token immediately upon account creation.
    """
    # 1. Check if username already exists
    existing_user_query = select(Patient).where(Patient.username == req.username)
    result = await db.execute(existing_user_query)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The username '{req.username}' is already taken. Please choose a different username."
        )

    # 2. Check if email already exists
    if req.email:
        existing_email_query = select(Patient).where(Patient.email == req.email)
        res_email = await db.execute(existing_email_query)
        if res_email.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An account with the email '{req.email}' already exists. Please sign in instead."
            )

    # 3. Hash password with bcrypt
    hashed = hash_password(req.password)

    # 4. Clean phone number if provided
    clean_phone = req.phone.strip() if req.phone else None
    if clean_phone and not clean_phone.startswith("+91") and len(clean_phone) == 10:
        clean_phone = f"+91 {clean_phone}"

    # 5. Create new patient record with safe schema defaults
    patient = Patient(
        name=req.name.strip(),
        username=req.username,
        email=req.email,
        phone=clean_phone,
        hashed_password=hashed,
        dob=date(2000, 1, 1),
        sex="Not Specified",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(patient)
    await db.flush()

    # 6. Audit Trail logging
    audit = AuditLog(
        patient_id=patient.id,
        action="PATIENT_REGISTERED",
        entity="Patient",
        entity_id=patient.id,
        actor="user_self_registration",
        after_state={
            "name": patient.name,
            "username": patient.username,
            "email": patient.email,
            "auth_method": "username_password"
        },
        timestamp=datetime.now(timezone.utc)
    )
    db.add(audit)
    await db.commit()
    await db.refresh(patient)

    # 7. Issue JWT token
    token_payload = {
        "sub": patient.id,
        "username": patient.username,
        "name": patient.name,
        "email": patient.email,
        "role": "patient"
    }
    access_token = create_access_token(token_payload)

    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 86400,
        "patient": PatientAuthProfile(
            id=patient.id,
            name=patient.name,
            username=patient.username,
            email=patient.email,
            phone=patient.phone,
            dob=str(patient.dob) if patient.dob else None,
            sex=patient.sex,
            abha_id=patient.abha_id,
            state=patient.state,
            city=patient.city
        )
    }


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticates a patient using Username or Email and Password.
    Returns signed JWT access token and user profile.
    """
    identifier = req.username_or_email.strip().lower()

    # Find patient by username or email
    query = select(Patient).where(
        or_(
            Patient.username == identifier,
            Patient.email == identifier
        )
    )
    result = await db.execute(query)
    patient = result.scalars().first()

    # Verify credentials
    if not patient or not patient.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(req.password, patient.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Audit Trail logging
    audit = AuditLog(
        patient_id=patient.id,
        action="PATIENT_LOGIN",
        entity="Patient",
        entity_id=patient.id,
        actor="user_password_login",
        after_state={
            "username": patient.username,
            "remember_me": req.remember_me
        },
        timestamp=datetime.now(timezone.utc)
    )
    db.add(audit)
    await db.commit()

    # Issue JWT
    expires_delta = timedelta(days=30) if req.remember_me else timedelta(days=1)
    token_payload = {
        "sub": patient.id,
        "username": patient.username,
        "name": patient.name,
        "email": patient.email,
        "role": "patient"
    }
    access_token = create_access_token(token_payload, expires_delta=expires_delta)

    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": int(expires_delta.total_seconds() // 60),
        "patient": PatientAuthProfile(
            id=patient.id,
            name=patient.name,
            username=patient.username,
            email=patient.email,
            phone=patient.phone,
            dob=str(patient.dob) if patient.dob else None,
            sex=patient.sex,
            abha_id=patient.abha_id,
            state=patient.state,
            city=patient.city
        )
    }


@router.get("/me")
async def get_current_user_profile(
    patient_id: Optional[str] = Depends(get_optional_authenticated_patient_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns profile information for the currently authenticated patient.
    Requires a valid Bearer token.
    """
    if not patient_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Valid Bearer token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    query = select(Patient).where(Patient.id == patient_id)
    result = await db.execute(query)
    patient = result.scalars().first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found for authenticated user.",
        )

    patient_dict = {
        "id": patient.id,
        "name": patient.name,
        "username": patient.username,
        "email": patient.email,
        "dob": str(patient.dob) if patient.dob else None,
        "sex": patient.sex,
        "phone": patient.phone,
        "abha_id": patient.abha_id,
        "state": patient.state,
        "city": patient.city,
        "emergency_contact": patient.emergency_contact,
    }

    return {
        "authenticated": True,
        **patient_dict,
        "patient": patient_dict
    }

