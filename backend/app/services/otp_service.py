import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import httpx
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import generate_numeric_otp, hash_otp, verify_otp_hash
from app.models.otp_verification import OTPVerification

logger = logging.getLogger("medlens.otp")


def normalize_indian_phone(phone: str) -> str:
    """
    Strips country code, spaces, dashes, and returns normalized 10-digit Indian mobile.
    Validates that number starts with 6, 7, 8, or 9.
    """
    clean = re.sub(r"\D", "", phone)
    if clean.startswith("91") and len(clean) == 12:
        clean = clean[2:]
    elif clean.startswith("0") and len(clean) == 11:
        clean = clean[1:]

    if not re.match(r"^[6-9]\d{9}$", clean):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Indian mobile number. Must be a 10-digit number starting with 6, 7, 8, or 9."
        )
    return clean


class SMSGatewayService:
    """
    Extensible, provider-agnostic SMS & WhatsApp gateway service.
    Supports Fast2SMS, Twilio Verify, MSG91, and Console dev fallback.
    """

    @classmethod
    async def send_otp(cls, phone_10digit: str, otp: str) -> Dict[str, Any]:
        provider = (settings.OTP_PROVIDER or "console").lower().strip()

        # Fast2SMS: Indian DLT-compliant Quick SMS / OTP route
        if provider == "fast2sms" and settings.FAST2SMS_API_KEY:
            return await cls._send_via_fast2sms(phone_10digit, otp)

        # Twilio Verify v2
        elif provider == "twilio" and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            return await cls._send_via_twilio(phone_10digit, otp)

        # MSG91
        elif provider == "msg91" and settings.MSG91_AUTH_KEY:
            return await cls._send_via_msg91(phone_10digit, otp)

        # Console / Local Staging Fallback
        else:
            return cls._send_via_console(phone_10digit, otp)

    @classmethod
    async def _send_via_fast2sms(cls, phone_10digit: str, otp: str) -> Dict[str, Any]:
        url = "https://www.fast2sms.com/dev/bulkV2"
        headers = {
            "authorization": settings.FAST2SMS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "variables_values": otp,
            "route": "otp",
            "numbers": phone_10digit
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                data = res.json()
                if res.status_code == 200 and data.get("return") is True:
                    logger.info(f"[Fast2SMS] Dispatched OTP to +91 {phone_10digit}")
                    return {"provider": "fast2sms", "status": "sent", "message": "OTP delivered via Fast2SMS"}
                else:
                    logger.error(f"[Fast2SMS Error] {data}")
                    # Graceful fallback to console for test/staging safety if credit/DLT issue
                    return cls._send_via_console(phone_10digit, otp, note="Fast2SMS failed, falling back to console")
        except Exception as e:
            logger.error(f"[Fast2SMS Network Error] {e}")
            return cls._send_via_console(phone_10digit, otp, note=f"Fast2SMS error: {e}")

    @classmethod
    async def _send_via_twilio(cls, phone_10digit: str, otp: str) -> Dict[str, Any]:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
        auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        data = {
            "To": f"+91{phone_10digit}",
            "From": settings.TWILIO_VERIFY_SERVICE_SID,
            "Body": f"Your MedLens verification code is {otp}. Valid for 5 minutes. Do not share this OTP."
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, data=data, auth=auth)
                if res.status_code in (200, 201):
                    logger.info(f"[Twilio] Dispatched OTP to +91 {phone_10digit}")
                    return {"provider": "twilio", "status": "sent", "message": "OTP delivered via Twilio"}
                else:
                    return cls._send_via_console(phone_10digit, otp, note="Twilio failed, logged to console")
        except Exception as e:
            return cls._send_via_console(phone_10digit, otp, note=f"Twilio error: {e}")

    @classmethod
    async def _send_via_msg91(cls, phone_10digit: str, otp: str) -> Dict[str, Any]:
        url = "https://api.msg91.com/api/v5/otp"
        params = {
            "template_id": "medlens_otp",
            "mobile": f"91{phone_10digit}",
            "authkey": settings.MSG91_AUTH_KEY,
            "otp": otp
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, params=params)
                if res.status_code == 200:
                    return {"provider": "msg91", "status": "sent"}
                return cls._send_via_console(phone_10digit, otp)
        except Exception:
            return cls._send_via_console(phone_10digit, otp)

    @classmethod
    def _send_via_console(cls, phone_10digit: str, otp: str, note: Optional[str] = None) -> Dict[str, Any]:
        banner = (
            f"\n+=============================================================+\n"
            f"| [MEDLENS LIVE OTP SERVICE] {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}       |\n"
            f"| Target Mobile:  +91 {phone_10digit}                                  |\n"
            f"| 6-Digit OTP:    *** {otp} ***                                |\n"
            f"| Validity TTL:   5 Minutes (300 seconds)                     |\n"
            f"| Max Attempts:   3 attempts allowed                          |\n"
            f"+=============================================================+\n"
        )
        print(banner, flush=True)
        return {
            "provider": "console",
            "status": "logged_to_console",
            "message": "OTP printed to server console (OTP_PROVIDER=console)",
            "note": note
        }


class OTPManager:
    """
    Coordinates rate limiting, salted hashing, database persistence, and attempt validation.
    """

    @staticmethod
    async def check_rate_limit(phone: str, db: AsyncSession, limit: int = 3, window_minutes: int = 15):
        """
        Enforces maximum 3 OTP dispatches per phone number in 15 minutes.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
        query = select(func.count(OTPVerification.id)).where(
            OTPVerification.phone == phone,
            OTPVerification.created_at >= cutoff
        )
        result = await db.execute(query)
        recent_count = result.scalar() or 0

        if recent_count >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many OTP requests for this number. Maximum {limit} requests allowed per {window_minutes} minutes. Please wait before retrying."
            )

    @staticmethod
    async def create_and_send_otp(phone: str, db: AsyncSession, client_ip: Optional[str] = None) -> Dict[str, Any]:
        normalized_phone = normalize_indian_phone(phone)

        # 1. Enforce Rate Limiting
        await OTPManager.check_rate_limit(normalized_phone, db, limit=3, window_minutes=15)

        # 2. Generate Cryptographic 6-digit OTP
        otp_code = generate_numeric_otp(6)

        # 3. Hash OTP with salt
        hashed = hash_otp(otp_code, normalized_phone)

        # 4. Save to Database with 5-minute TTL
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=5)

        verification_record = OTPVerification(
            phone=normalized_phone,
            hashed_otp=hashed,
            attempts=0,
            max_attempts=3,
            is_verified=False,
            expires_at=expires_at,
            created_at=now,
            client_ip=client_ip
        )
        db.add(verification_record)
        await db.commit()
        await db.refresh(verification_record)

        # 5. Dispatch through Gateway Service
        dispatch_result = await SMSGatewayService.send_otp(normalized_phone, otp_code)

        response = {
            "success": True,
            "request_id": verification_record.request_id,
            "phone": f"+91 {normalized_phone}",
            "expires_in": 300,
            "provider": dispatch_result.get("provider")
        }

        # For development / console mode, provide dev_otp for rapid testing
        if settings.ENVIRONMENT != "production" or settings.OTP_PROVIDER == "console":
            response["dev_otp"] = otp_code

        return response

    @staticmethod
    async def verify_otp(phone: str, otp: str, request_id: str, db: AsyncSession) -> OTPVerification:
        normalized_phone = normalize_indian_phone(phone)
        clean_otp = otp.strip()

        if len(clean_otp) != 6 or not clean_otp.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP must be a 6-digit numeric code."
            )

        query = select(OTPVerification).where(
            OTPVerification.request_id == request_id,
            OTPVerification.phone == normalized_phone
        )
        result = await db.execute(query)
        record = result.scalars().first()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Verification request not found or does not match mobile number. Please request a new OTP."
            )

        if record.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This OTP has already been verified."
            )

        if record.is_expired():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This OTP has expired (5-minute limit). Please request a fresh code."
            )

        if record.attempts >= record.max_attempts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum verification attempts exceeded. This OTP request is now invalid. Please request a fresh code."
            )

        # Verify hash
        is_valid = verify_otp_hash(clean_otp, normalized_phone, record.hashed_otp)
        if not is_valid:
            record.attempts += 1
            await db.commit()
            remaining = record.max_attempts - record.attempts
            if remaining <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Incorrect OTP. Maximum verification attempts exceeded. Please request a fresh code."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Incorrect OTP. {remaining} attempt{'s' if remaining > 1 else ''} remaining."
                )

        # Mark verified
        record.is_verified = True
        await db.commit()
        await db.refresh(record)
        return record
