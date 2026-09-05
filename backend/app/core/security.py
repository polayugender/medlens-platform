import bcrypt
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.db.session import get_db

ALGORITHM = "HS256"
security_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """
    Hashes a plain text password using bcrypt with a randomized salt.
    """
    pw_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a stored bcrypt hash.
    """
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def generate_numeric_otp(digits: int = 6) -> str:
    """
    Generates a cryptographically secure numeric OTP using secrets.randbelow().
    """
    min_val = 10 ** (digits - 1)
    max_val = (10 ** digits) - 1
    return str(secrets.randbelow(max_val - min_val + 1) + min_val)


def hash_otp(otp: str, phone: str) -> str:
    """
    Computes a salted HMAC-SHA256 digest of the OTP and phone number.
    Never stores plaintext OTPs in the database.
    """
    salt = settings.SECRET_KEY.encode("utf-8")
    payload = f"{phone}:{otp}".encode("utf-8")
    return hmac.new(salt, payload, hashlib.sha256).hexdigest()


def verify_otp_hash(plain_otp: str, phone: str, stored_hash: str) -> bool:
    """
    Constant-time comparison of computed OTP hash against stored hash.
    """
    computed = hash_otp(plain_otp, phone)
    return hmac.compare_digest(computed, stored_hash)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Issues a signed JWT access token.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT access token.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token has expired. Please sign in again with OTP.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_authenticated_patient_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> Optional[str]:
    """
    Extracts the patient_id / sub from JWT if provided; returns None if not provided (for sandbox/demo).
    """
    if not credentials or not credentials.credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    return payload.get("sub") or payload.get("patient_id")
