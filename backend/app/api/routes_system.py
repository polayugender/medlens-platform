import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db, AsyncSessionLocal
from app.config import settings
from app.models.patient import Patient
from app.models.intake import IntakeRecord
from app.models.report import MedicalReport
from app.models.extracted_test import ExtractedTest
from app.models.summary import Summary
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/system", tags=["System"])

@router.post("/reset")
async def reset_system_data(db: AsyncSession = Depends(get_db)):
    """
    Clears all patients, clinical records, extracted tests, summaries,
    audit logs, and uploaded report/preview storage files.
    Prepares the application cleanly for new users.
    """
    try:
        # Delete from DB tables in topological order
        for table in [AuditLog, ExtractedTest, Summary, MedicalReport, IntakeRecord, Patient]:
            await db.execute(table.__table__.delete())
        await db.commit()

        # Clean storage directories
        for directory in [settings.REPORTS_DIR, settings.PREVIEWS_DIR]:
            if directory.exists():
                for item in directory.iterdir():
                    if item.is_file():
                        try:
                            item.unlink()
                        except Exception as e:
                            print(f"Failed to delete {item}: {e}")

        return {
            "status": "success",
            "message": "All clinical records and storage data cleared successfully. MedLens is ready for new users.",
            "cleared_tables": ["AuditLog", "ExtractedTest", "Summary", "MedicalReport", "IntakeRecord", "Patient"]
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset database: {str(e)}"
        )

@router.post("/seed-demo")
async def seed_demo_data():
    """
    Loads realistic clinical demo profiles (Eleanor Vance & Arthur Pendelton)
    with diagnostic reports and conflicts for demonstration purposes.
    """
    try:
        from seed.seed_data import seed
        await seed()
        return {
            "status": "success",
            "message": "Sample clinical demo data loaded successfully."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to seed demo data: {str(e)}"
        )
