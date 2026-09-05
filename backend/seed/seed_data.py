import asyncio
import os
import shutil
from datetime import date, datetime, timezone
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import init_db, AsyncSessionLocal
from app.config import settings
from app.models.patient import Patient
from app.models.intake import IntakeRecord
from app.models.report import MedicalReport
from app.models.extracted_test import ExtractedTest
from app.models.summary import Summary
from app.models.audit_log import AuditLog
from app.core.provenance import SourceProvenance, FlagCategory
from app.core.flag_calculator import parse_reference_range, compute_flag
from app.services.pdf_parser import parse_pdf_document
from app.services.ai_extractor import extract_structured_tests_from_report
from app.services.summarizer import generate_patient_summary
from seed.generate_sample_pdfs import create_cmp_report, create_cbc_report, create_lipid_report

async def seed():
    print("[INIT] Initializing MedLens database...")
    await init_db()

    # Generate sample PDFs
    samples_dir = Path(__file__).resolve().parent / "sample_reports"
    samples_dir.mkdir(parents=True, exist_ok=True)
    
    cmp_path = samples_dir / "sample_cmp_report.pdf"
    cbc_path = samples_dir / "sample_cbc_report.pdf"
    lipid_path = samples_dir / "sample_lipid_panel.pdf"

    print("[PDF] Generating realistic clinical PDFs via ReportLab...")
    create_cmp_report(cmp_path)
    create_cbc_report(cbc_path)
    create_lipid_report(lipid_path)

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        existing = await db.execute(Patient.__table__.select())
        if existing.first():
            print("Database already contains records. Clearing for fresh seed...")
            for table in [AuditLog, ExtractedTest, Summary, MedicalReport, IntakeRecord, Patient]:
                await db.execute(table.__table__.delete())
            await db.commit()

        print("[PATIENT 1] Creating Patient 1: Eleanor Vance...")
        p1 = Patient(
            name="Eleanor Vance",
            dob=date(1978, 4, 14),
            sex="Female"
        )
        db.add(p1)
        await db.flush()

        # P1 Intake Record (Source: user_input)
        intake1 = IntakeRecord(
            patient_id=p1.id,
            version=1,
            age=48,
            sex="Female",
            symptoms=["Occasional mild fatigue", "Intermittent morning dizziness"],
            existing_conditions=["Essential Hypertension", "Mild Hyperlipidemia"],
            allergies=["Penicillin", "Sulfa drugs"], # Potential cross-reactivity with Amoxicillin!
            medications=[
                {"name": "Lisinopril", "dosage": "10mg", "frequency": "Daily", "route": "Oral"},
                {"name": "Amoxicillin", "dosage": "500mg", "frequency": "Every 8 hours", "route": "Oral"} # Deliberate conflict for safety detection demo
            ],
            source=SourceProvenance.USER_INPUT.value
        )
        db.add(intake1)
        await db.flush()

        # Seed Report 1: CMP for Eleanor
        cmp_dest = settings.REPORTS_DIR / f"{p1.id}_cmp.pdf"
        shutil.copyfile(cmp_path, cmp_dest)
        parsed_cmp = parse_pdf_document(cmp_dest)
        cmp_extracted = await extract_structured_tests_from_report(parsed_cmp["raw_text"])

        rep1 = MedicalReport(
            id=f"rep-cmp-{p1.id[:8]}",
            patient_id=p1.id,
            original_filename="Comprehensive_Metabolic_Panel_Aug2026.pdf",
            file_url=f"/storage/reports/{cmp_dest.name}",
            file_type="pdf",
            report_date=date(2026, 8, 15),
            report_type="Comprehensive Metabolic Panel (CMP)",
            facility_name="Apex Clinical Laboratory",
            raw_text=parsed_cmp["raw_text"],
            page_count=parsed_cmp["page_count"]
        )
        db.add(rep1)
        await db.flush()

        p1_tests = []
        for item in cmp_extracted.extracted_tests:
            low_b, high_b = parse_reference_range(item.reference_range_raw)
            flag = compute_flag(item.value_numeric, low_b, high_b, item.value)
            t = ExtractedTest(
                report_id=rep1.id,
                patient_id=p1.id,
                test_name=item.test_name,
                value=item.value,
                value_numeric=item.value_numeric,
                unit=item.unit,
                reference_range_raw=item.reference_range_raw,
                reference_range_low=low_b,
                reference_range_high=high_b,
                flag=flag.value,
                source=SourceProvenance.AI_EXTRACTED.value,
                verified=True, # Eleanor's CMP is verified
                verified_by="Dr. M. Reed, MD",
                verified_at=datetime.now(timezone.utc),
                raw_snippet=item.raw_snippet,
                confidence_score=item.confidence
            )
            db.add(t)
            p1_tests.append({
                "test_name": t.test_name,
                "value": t.value,
                "unit": t.unit,
                "reference_range_raw": t.reference_range_raw,
                "flag": t.flag
            })

        # Seed Report 2: Lipid Panel for Eleanor
        lipid_dest = settings.REPORTS_DIR / f"{p1.id}_lipid.pdf"
        shutil.copyfile(lipid_path, lipid_dest)
        parsed_lipid = parse_pdf_document(lipid_dest)
        lipid_extracted = await extract_structured_tests_from_report(parsed_lipid["raw_text"])

        rep2 = MedicalReport(
            id=f"rep-lipid-{p1.id[:8]}",
            patient_id=p1.id,
            original_filename="Lipid_Profile_Aug2026.pdf",
            file_url=f"/storage/reports/{lipid_dest.name}",
            file_type="pdf",
            report_date=date(2026, 8, 15),
            report_type="Lipid Panel",
            facility_name="St. Jude Hospital Pathology Services",
            raw_text=parsed_lipid["raw_text"],
            page_count=parsed_lipid["page_count"]
        )
        db.add(rep2)
        await db.flush()

        for item in lipid_extracted.extracted_tests:
            low_b, high_b = parse_reference_range(item.reference_range_raw)
            flag = compute_flag(item.value_numeric, low_b, high_b, item.value)
            t = ExtractedTest(
                report_id=rep2.id,
                patient_id=p1.id,
                test_name=item.test_name,
                value=item.value,
                value_numeric=item.value_numeric,
                unit=item.unit,
                reference_range_raw=item.reference_range_raw,
                reference_range_low=low_b,
                reference_range_high=high_b,
                flag=flag.value,
                source=SourceProvenance.AI_EXTRACTED.value,
                verified=True,
                verified_by="Dr. M. Reed, MD",
                verified_at=datetime.now(timezone.utc),
                raw_snippet=item.raw_snippet,
                confidence_score=item.confidence
            )
            db.add(t)
            p1_tests.append({
                "test_name": t.test_name,
                "value": t.value,
                "unit": t.unit,
                "reference_range_raw": t.reference_range_raw,
                "flag": t.flag
            })

        # Summary for Eleanor (Source: ai_generated)
        summary_text_p1 = await generate_patient_summary(
            patient_data={"name": p1.name, "dob": str(p1.dob), "sex": p1.sex},
            intake_data={
                "age": intake1.age, "sex": intake1.sex,
                "symptoms": intake1.symptoms,
                "existing_conditions": intake1.existing_conditions,
                "allergies": intake1.allergies,
                "medications": intake1.medications
            },
            verified_tests=p1_tests
        )

        sum1 = Summary(
            patient_id=p1.id,
            version=1,
            summary_text=summary_text_p1,
            based_on_report_ids=[rep1.id, rep2.id],
            based_on_intake_version=1,
            source=SourceProvenance.AI_GENERATED.value
        )
        db.add(sum1)
        await db.flush()

        # Audit logs for Eleanor
        db.add(AuditLog(patient_id=p1.id, actor="Eleanor Vance", action="PATIENT_CREATED", entity="Patient", entity_id=p1.id))
        db.add(AuditLog(patient_id=p1.id, actor="Eleanor Vance", action="INTAKE_SUBMITTED", entity="IntakeRecord", entity_id=intake1.id))
        db.add(AuditLog(patient_id=p1.id, actor="AI Pipeline", action="REPORT_UPLOADED_AND_PARSED", entity="MedicalReport", entity_id=rep1.id))
        db.add(AuditLog(patient_id=p1.id, actor="Dr. M. Reed, MD", action="TESTS_BATCH_VERIFIED", entity="ExtractedTest", entity_id=p1.id))
        db.add(AuditLog(patient_id=p1.id, actor="AI Summarizer", action="SUMMARY_GENERATED", entity="Summary", entity_id=sum1.id))

        # ---------------------------------------------------------------------
        print("[PATIENT 2] Creating Patient 2: Arthur Pendelton...")
        p2 = Patient(
            name="Arthur Pendelton",
            dob=date(1962, 11, 20),
            sex="Male"
        )
        db.add(p2)
        await db.flush()

        intake2 = IntakeRecord(
            patient_id=p2.id,
            version=1,
            age=63,
            sex="Male",
            symptoms=["Exertional shortness of breath", "Mild pallor"],
            existing_conditions=["Chronic Kidney Disease (Stage 2)", "Dyslipidemia"],
            allergies=["Aspirin"], # Deliberate conflict with Aspirin 81mg medication
            medications=[
                {"name": "Atorvastatin", "dosage": "20mg", "frequency": "Daily at bedtime", "route": "Oral"},
                {"name": "Aspirin", "dosage": "81mg", "frequency": "Daily", "route": "Oral"}
            ],
            source=SourceProvenance.USER_INPUT.value
        )
        db.add(intake2)
        await db.flush()

        # Seed CBC report for Arthur (left UNVERIFIED to demonstrate human-in-the-loop review workflow)
        cbc_dest = settings.REPORTS_DIR / f"{p2.id}_cbc.pdf"
        shutil.copyfile(cbc_path, cbc_dest)
        parsed_cbc = parse_pdf_document(cbc_dest)
        cbc_extracted = await extract_structured_tests_from_report(parsed_cbc["raw_text"])

        rep3 = MedicalReport(
            id=f"rep-cbc-{p2.id[:8]}",
            patient_id=p2.id,
            original_filename="Complete_Blood_Count_Differential_July2026.pdf",
            file_url=f"/storage/reports/{cbc_dest.name}",
            file_type="pdf",
            report_date=date(2026, 7, 22),
            report_type="Complete Blood Count (CBC)",
            facility_name="Quest Central Hematology Laboratory",
            raw_text=parsed_cbc["raw_text"],
            page_count=parsed_cbc["page_count"]
        )
        db.add(rep3)
        await db.flush()

        for item in cbc_extracted.extracted_tests:
            low_b, high_b = parse_reference_range(item.reference_range_raw)
            flag = compute_flag(item.value_numeric, low_b, high_b, item.value)
            t = ExtractedTest(
                report_id=rep3.id,
                patient_id=p2.id,
                test_name=item.test_name,
                value=item.value,
                value_numeric=item.value_numeric,
                unit=item.unit,
                reference_range_raw=item.reference_range_raw,
                reference_range_low=low_b,
                reference_range_high=high_b,
                flag=flag.value,
                source=SourceProvenance.AI_EXTRACTED.value,
                verified=False, # Demonstrates unverified status awaiting user review!
                raw_snippet=item.raw_snippet,
                confidence_score=item.confidence
            )
            db.add(t)

        db.add(AuditLog(patient_id=p2.id, actor="Arthur Pendelton", action="PATIENT_CREATED", entity="Patient", entity_id=p2.id))
        db.add(AuditLog(patient_id=p2.id, actor="Arthur Pendelton", action="INTAKE_SUBMITTED", entity="IntakeRecord", entity_id=intake2.id))
        db.add(AuditLog(patient_id=p2.id, actor="AI Pipeline", action="REPORT_UPLOADED_AND_PARSED", entity="MedicalReport", entity_id=rep3.id))

        # ---------------------------------------------------------------------
        print("[PATIENT 3] Creating Patient 3: Maya Rodriguez...")
        p3 = Patient(
            name="Maya Rodriguez",
            dob=date(1992, 6, 8),
            sex="Female"
        )
        db.add(p3)
        await db.flush()

        intake3 = IntakeRecord(
            patient_id=p3.id,
            version=1,
            age=34,
            sex="Female",
            symptoms=["Fatigue", "Cold intolerance", "Dry skin"],
            existing_conditions=["Hypothyroidism"],
            allergies=["Latex", "Codeine"],
            medications=[
                {"name": "Levothyroxine", "dosage": "75mcg", "frequency": "Daily in morning", "route": "Oral"}
            ],
            source=SourceProvenance.USER_INPUT.value
        )
        db.add(intake3)
        await db.flush()

        db.add(AuditLog(patient_id=p3.id, actor="Maya Rodriguez", action="PATIENT_CREATED", entity="Patient", entity_id=p3.id))
        db.add(AuditLog(patient_id=p3.id, actor="Maya Rodriguez", action="INTAKE_SUBMITTED", entity="IntakeRecord", entity_id=intake3.id))

        await db.commit()
        print("[SUCCESS] Database successfully seeded with 3 realistic patients, sample reports, and audit trails!")

if __name__ == "__main__":
    asyncio.run(seed())
