"""
MedLens Database State & Data Integrity Inspector
-------------------------------------------------
Inspects SQLite tables, patient records, extracted lab tests,
verified/unverified distribution, summaries, and immutable audit logs.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "medlens.db"

def inspect():
    if not DB_PATH.exists():
        print(f"[ERROR] Database file not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"\n========================================================")
    print(f"  MEDLENS DATABASE INSPECTION REPORT")
    print(f"  Path: {DB_PATH}")
    print(f"========================================================\n")

    # Table names and row counts
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [r[0] for r in cursor.fetchall()]
    print("Database Tables & Row Counts:")
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        count = cursor.fetchone()[0]
        print(f"  - {t:<20}: {count} records")

    # Patient details
    print("\n--------------------------------------------------------")
    print("Registered Patients:")
    print("--------------------------------------------------------")
    cursor.execute("SELECT id, name, dob, sex FROM patients ORDER BY created_at ASC")
    patients = cursor.fetchall()
    for p_id, name, dob, sex in patients:
        cursor.execute("SELECT COUNT(*) FROM intake_records WHERE patient_id = ?", (p_id,))
        intake_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM medical_reports WHERE patient_id = ?", (p_id,))
        report_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM extracted_tests WHERE patient_id = ? AND verified = 1", (p_id,))
        verified_tests = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM extracted_tests WHERE patient_id = ? AND verified = 0", (p_id,))
        unverified_tests = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM summaries WHERE patient_id = ?", (p_id,))
        summary_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM audit_logs WHERE patient_id = ?", (p_id,))
        audit_count = cursor.fetchone()[0]

        print(f"\n* {name} ({sex}, DOB: {dob})")
        print(f"  Patient ID: {p_id}")
        print(f"  - Intake Records  : {intake_count}")
        print(f"  - Uploaded Reports: {report_count}")
        print(f"  - Extracted Tests : {verified_tests + unverified_tests} total ({verified_tests} verified, {unverified_tests} pending)")
        print(f"  - AI Summaries    : {summary_count}")
        print(f"  - Audit Trail Log : {audit_count} entries")

    # Extracted tests flag breakdown
    print("\n--------------------------------------------------------")
    print("Extracted Tests Flag Distribution:")
    print("--------------------------------------------------------")
    cursor.execute("SELECT flag, COUNT(*) FROM extracted_tests GROUP BY flag")
    flags = cursor.fetchall()
    for flag, cnt in flags:
        print(f"  - {flag.upper():<12}: {cnt} tests")

    # Recent audit trail entries
    print("\n--------------------------------------------------------")
    print("Recent Audit Trail Events (Latest 8):")
    print("--------------------------------------------------------")
    cursor.execute("SELECT timestamp, actor, action, entity, entity_id FROM audit_logs ORDER BY timestamp DESC LIMIT 8")
    logs = cursor.fetchall()
    for ts, actor, action, entity, entity_id in logs:
        print(f"  [{ts}] {actor:<25} -> {action:<22} ({entity})")

    print("\n========================================================\n")
    conn.close()

if __name__ == "__main__":
    inspect()
