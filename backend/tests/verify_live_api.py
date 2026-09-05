import urllib.request
import json
import sys

BASE = "http://127.0.0.1:8000/api"

def get(path):
    req = urllib.request.Request(f"{BASE}{path}", headers={"User-Agent": "MedLens-Verifier/1.0"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def post(path, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def put(path, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers={"Content-Type": "application/json"}, method="PUT")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def verify_all():
    print("[TEST] Testing /api/health...")
    health = get("/health")
    assert health["status"] == "healthy"
    print("  -> Health OK:", health)

    print("[TEST] Testing /api/patients...")
    patients = get("/patients")
    assert len(patients) >= 3
    print(f"  -> {len(patients)} patients found:")
    for p in patients:
        print(f"     - {p['name']} ({p['sex']}, DOB: {p['dob']}, ID: {p['id']})")

    # Test Eleanor Vance
    eleanor = next(p for p in patients if "Eleanor" in p["name"])
    e_id = eleanor["id"]
    print(f"\n[TEST] Verifying Eleanor Vance ({e_id})...")

    intake = get(f"/patients/{e_id}/intake")
    print(f"  -> Intake version: {intake['version']}, allergies: {intake['allergies']}, meds: {len(intake['medications'])}")

    reports = get(f"/patients/{e_id}/reports")
    print(f"  -> Uploaded reports count: {len(reports)}")
    assert len(reports) >= 2

    tests = get(f"/patients/{e_id}/tests")
    verified_count = sum(1 for t in tests if t["verified"])
    print(f"  -> Total extracted tests: {len(tests)}, Verified: {verified_count}")
    assert len(tests) >= 20

    summary = get(f"/patients/{e_id}/summary")
    print(f"  -> Summary version {summary['version']} length: {len(summary['summary_text'])} chars")
    print(f"  -> Source provenance: {summary['source']}")
    assert "Consult" in summary["disclaimer"] or "diagnosis" in summary["disclaimer"]

    conflicts = get(f"/patients/{e_id}/conflicts")
    print(f"  -> Clinical conflicts detected: {conflicts['total']}")
    # Eleanor has penicillin allergy + amoxicillin active med
    allergy_alerts = [c for c in conflicts["conflicts"] if c["category"] == "Allergy Contradiction"]
    print(f"  -> Allergy contradiction alerts: {len(allergy_alerts)}")
    assert len(allergy_alerts) >= 1
    print(f"     Title: {allergy_alerts[0]['title']}")

    trends = get(f"/patients/{e_id}/trends")
    print(f"  -> Trend groups: {len(trends)}")

    # Test Arthur Pendelton (Unverified tests verification workflow)
    arthur = next(p for p in patients if "Arthur" in p["name"])
    a_id = arthur["id"]
    print(f"\n[TEST] Verifying Arthur Pendelton ({a_id}) - Human-in-the-loop...")
    a_tests = get(f"/patients/{a_id}/tests")
    unverified_a = [t for t in a_tests if not t["verified"]]
    
    # If already verified in a previous test run, reset Arthur's tests to unverified for test repeatability
    if len(unverified_a) == 0 and len(a_tests) > 0:
        print("  -> (Arthur tests were previously verified - resetting to unverified state for verification test)")
        for t in a_tests:
            put(f"/tests/{t['id']}", {"verified": False})
        a_tests = get(f"/patients/{a_id}/tests")
        unverified_a = [t for t in a_tests if not t["verified"]]

    print(f"  -> Unverified tests before batch verify: {len(unverified_a)}")
    assert len(unverified_a) > 0

    # Simulate user verifying all pending tests for Arthur
    batch_payload = {
        "verified_by": "Dr. Sarah Lin, MD",
        "tests": [
            {
                "id": t["id"],
                "test_name": t["test_name"],
                "value": t["value"],
                "value_numeric": t["value_numeric"],
                "unit": t["unit"],
                "reference_range_raw": t["reference_range_raw"]
            }
            for t in unverified_a
        ]
    }
    verify_res = post(f"/patients/{a_id}/tests/verify-batch", batch_payload)
    print(f"  -> Batch verify confirmed: {len(verify_res)} tests verified!")
    assert all(t["verified"] for t in verify_res)

    # Test Arthur summary generation
    print("  -> Triggering summary generation for Arthur...")
    a_summary = post(f"/patients/{a_id}/summary", {"patient_id": a_id, "regenerate": True})
    print(f"  -> Generated Arthur summary version {a_summary['version']}: {a_summary['summary_text'][:120]}...")

    # Test Audit Trail
    audit_logs = get(f"/patients/{a_id}/audit-logs")
    print(f"  -> Audit trail events for Arthur: {len(audit_logs)}")
    assert any(log["action"] == "TESTS_BATCH_VERIFIED" for log in audit_logs)

    # Test Export
    export_data = get(f"/patients/{a_id}/export")
    print(f"  -> Export JSON contains: {list(export_data.keys())}")
    assert export_data["metadata"]["system"] == "MedLens AI-Powered Clinical Intelligence"

    # Restore Arthur's unverified status so demo UI remains ready for Human-in-the-loop review
    print("  -> Restoring Arthur's tests to unverified state for UI demo...")
    for t in a_tests:
        put(f"/tests/{t['id']}", {"verified": False})

    print("\n[ALL TESTS PASSED SUCCESSFULLY!]")

if __name__ == "__main__":
    verify_all()
