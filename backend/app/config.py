import os
from pathlib import Path
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "MedLens"
    API_V1_STR: str = "/api"
    
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    STORAGE_DIR: Path = Path(__file__).resolve().parent.parent.parent / "storage"
    REPORTS_DIR: Path = Path(__file__).resolve().parent.parent.parent / "storage" / "reports"
    PREVIEWS_DIR: Path = Path(__file__).resolve().parent.parent.parent / "storage" / "previews"
    
    # Environment & Server
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PORT: int = int(os.getenv("PORT", "8000"))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "medlens_production_secret_key_change_in_production_381920")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite+aiosqlite:///{Path(__file__).resolve().parent.parent}/medlens.db"
    )

    # Live SMS / OTP Gateway Configuration
    OTP_PROVIDER: str = os.getenv("OTP_PROVIDER", "console")  # fast2sms | twilio | msg91 | console
    FAST2SMS_API_KEY: str = os.getenv("FAST2SMS_API_KEY", "")
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_VERIFY_SERVICE_SID: str = os.getenv("TWILIO_VERIFY_SERVICE_SID", "")
    MSG91_AUTH_KEY: str = os.getenv("MSG91_AUTH_KEY", "")

    # AI API Keys (Optional - gracefully falls back to deterministic extraction engine)
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

settings = Settings()

# Ensure storage directories exist
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
settings.PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
