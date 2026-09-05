import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.session import AsyncSessionLocal
from app.config import settings
from app.models.patient import Patient
from app.models.intake import IntakeRecord
from app.models.report import MedicalReport
from app.models.extracted_test import ExtractedTest
from app.models.summary import Summary
from app.models.audit_log import AuditLog

async def clear_all_data():
    print("=" * 60)
    print("[PURGE] MEDLENS DATA PURGE: Resetting system for new users...")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        tables = [AuditLog, ExtractedTest, Summary, MedicalReport, IntakeRecord, Patient]
        for table in tables:
            table_name = table.__tablename__
            result = await db.execute(table.__table__.delete())
            print(f"  [x] Cleared table: {table_name}")
        await db.commit()

    # Clean storage directories
    cleaned_count = 0
    for directory in [settings.REPORTS_DIR, settings.PREVIEWS_DIR]:
        if directory.exists():
            for item in directory.iterdir():
                if item.is_file():
                    try:
                        item.unlink()
                        cleaned_count += 1
                    except Exception as e:
                        print(f"  [!] Failed to delete {item.name}: {e}")
    print(f"  [x] Removed {cleaned_count} files from storage/reports & storage/previews")

    print("\n[OK] SYSTEM PURGED: MedLens is now fresh and ready for new users!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(clear_all_data())
