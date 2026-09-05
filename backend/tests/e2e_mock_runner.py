"""
MedLens End-to-End Mock Runner & Fallback Verification Suite
-----------------------------------------------------------
This test runner executes complete end-to-end user flows against the MedLens backend
without requiring Playwright or a browser display server. It can be run in headless,
restricted, or CI/CD environments to validate full platform integrity.
"""

import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000/api"

class TestColor:
    OK = "\033[92m"
    WARN = "\033[93m"
    FAIL = "\033[91m"
    BOLD = "\033[1m"
    END = "\033[0m"

def api_call(method: str, path: str, payload: dict = None):
    url = f"{BASE_URL}{path}"
    headers = {"User-Agent": "MedLens-E2E-Runner/1.0"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read()
            if "application/json" in content_type:
                return resp.status, json.loads(raw.decode("utf-8")), resp.headers
            return resp.status, raw, resp.headers
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        return e.code, err_body, e.headers

def run_e2e_mock():
    print(f"\n{TestColor.BOLD}========================================================")
    print("  MEDLENS CLINICAL INTELLIGENCE: END-TO-END MOCK RUNNER")
    print(f"========================================================{TestColor.END}\n")

    steps_passed = 0
    total_steps = 8

    # -------------------------------------------------------------------------
    # STEP 1: Health & System Diagnostics
    # -------------------------------------------------------------------------
    print(f"{TestColor.BOLD}[FLOW 1] System Health & Storage Readiness Check...{TestColor.END}")
    code, data, _ = api_call("GET", "/health")
    assert code == 200, f"Health check failed with HTTP {code}"
    assert data.get("status") == "healthy"
    assert data.get("storage_ready") is True
    print(f"  -> System: {data['system']} (v{data['version']})")
    print(f"  -> Storage Mount Status: Active")
    print(f"  {TestColor.OK}[PASS] FLOW 1 PASSED{TestColor.END}\n")
    steps_passed += 1

    # -------------------------------------------------------------------------
    # STEP 2: Patient Registry Audit
    # -------------------------------------------------------------------------
    print(f"{TestColor.BOLD}[FLOW 2] Patient Cohort Verification...{TestColor.END}")
    code, patients, _ = api_call("GET", "/patients")
    assert code == 200 and len(patients) >= 3
    patient_names = [p["name"] for p in patients]
    print(f"  -> Found {len(patients)} registered patients: {', '.join(patient_names)}")
    assert "Eleanor Vance" in patient_names
    assert "Arthur Pendelton" in patient_names
    assert "Maya Rodriguez" in patient_names
    eleanor = next(p for p in patients if p["name"] == "Eleanor Vance")
    arthur = next(p for p in patients if p["name"] == "Arthur Pendelton")
    maya = next(p for p in patients if p["name"] == "Maya Rodriguez")
    print(f"  {TestColor.OK}[PASS] FLOW 2 PASSED{TestColor.END}\n")
    steps_passed += 1

    # -------------------------------------------------------------------------
    # STEP 3: Eleanor Vance - Synthesized Record & Guardrail Inspection
    # -------------------------------------------------------------------------
    print(f"{TestColor.BOLD}[FLOW 3] Eleanor Vance: Unified Clinical Record & Non-Diagnostic Guardrails...{TestColor.END}")
    e_id = eleanor["id"]
    code, e_intake, _ = api_call("GET", f"/patients/{e_id}/intake")
    assert code == 200 and e_intake["version"] >= 1
    assert "Penicillin" in e_intake["allergies"]

    code, e_reports, _ = api_call("GET", f"/patients/{e_id}/reports")
    assert code == 200 and len(e_reports) >= 2
    print(f"  -> Linked Reports: {[r['report_type'] for r in e_reports]}")

    code, e_tests, _ = api_call("GET", f"/patients/{e_id}/tests")
    assert code == 200 and len(e_tests) >= 20
    high_tests = [t["test_name"] for t in e_tests if t["flag"] == "high"]
    print(f"  -> Total Extracted Tests: {len(e_tests)} (Elevated: {', '.join(high_tests)})")
    assert any(t["test_name"] == "Glucose, Fasting" and t["flag"] == "high" for t in e_tests)

    code, e_summary, _ = api_call("GET", f"/patients/{e_id}/summary")
    assert code == 200 and e_summary is not None
    assert "Consult" in e_summary["disclaimer"] or "diagnosis" in e_summary["disclaimer"]
    print(f"  -> Non-Diagnostic Summary: Verified (v{e_summary['version']}, {len(e_summary['summary_text'])} chars)")
    print(f"  {TestColor.OK}[PASS] FLOW 3 PASSED{TestColor.END}\n")
    steps_passed += 1

    # -------------------------------------------------------------------------
    # STEP 4: Eleanor Vance - Clinical Conflict Detection
    # -------------------------------------------------------------------------
    print(f"{TestColor.BOLD}[FLOW 4] Eleanor Vance: Clinical Safety Conflict Engine...{TestColor.END}")
    code, conflicts_data, _ = api_call("GET", f"/patients/{e_id}/conflicts")
    assert code == 200 and conflicts_data["total"] >= 1
    allergy_conflicts = [c for c in conflicts_data["conflicts"] if c["category"] == "Allergy Contradiction"]
    assert len(allergy_conflicts) >= 1
    print(f"  -> Active Safety Conflicts: {conflicts_data['total']}")
    print(f"  -> Cross-Reactivity Alert: {allergy_conflicts[0]['title']}")
    print(f"     Description: {allergy_conflicts[0]['description']}")
    print(f"  {TestColor.OK}[PASS] FLOW 4 PASSED{TestColor.END}\n")
    steps_passed += 1

    # -------------------------------------------------------------------------
    # STEP 5: Arthur Pendelton - Human-in-the-Loop Review & Batch Verification
    # -------------------------------------------------------------------------
    print(f"{TestColor.BOLD}[FLOW 5] Arthur Pendelton: Human-in-the-Loop Review Workflow...{TestColor.END}")
    a_id = arthur["id"]
    code, a_tests, _ = api_call("GET", f"/patients/{a_id}/tests")
    assert code == 200 and len(a_tests) > 0

    unverified = [t for t in a_tests if not t["verified"]]
    if len(unverified) == 0:
        print("  -> Resetting tests to unverified for test run...")
        for t in a_tests:
            api_call("PUT", f"/tests/{t['id']}", {"verified": False})
        _, a_tests, _ = api_call("GET", f"/patients/{a_id}/tests")
        unverified = [t for t in a_tests if not t["verified"]]

    print(f"  -> Pending Unverified Tests: {len(unverified)}")
    assert len(unverified) > 0

    # Step 5a: Human edits one value
    target_test = unverified[0]
    original_val = target_test["value"]
    code, edit_res, _ = api_call("PUT", f"/tests/{target_test['id']}", {
        "value": "7.2",
        "value_numeric": 7.2
    })
    assert code == 200
    print(f"  -> Clinician edited {target_test['test_name']}: '{original_val}' -> '7.2'")

    # Step 5b: Clinician batch-verifies all pending tests
    batch_payload = {
        "verified_by": "Dr. Sarah Lin, MD (Mock Runner)",
        "tests": [
            {
                "id": t["id"],
                "test_name": t["test_name"],
                "value": "7.2" if t["id"] == target_test["id"] else t["value"],
                "value_numeric": 7.2 if t["id"] == target_test["id"] else t["value_numeric"],
                "unit": t["unit"],
                "reference_range_raw": t["reference_range_raw"]
            }
            for t in unverified
        ]
    }
    code, verified_res, _ = api_call("POST", f"/patients/{a_id}/tests/verify-batch", batch_payload)
    assert code == 200 and len(verified_res) == len(unverified)
    assert all(t["verified"] for t in verified_res)
    print(f"  -> Batch verification confirmed: {len(verified_res)} tests approved into verified record")

    # Step 5c: Trigger summary generation
    code, a_sum, _ = api_call("POST", f"/patients/{a_id}/summary", {"patient_id": a_id, "regenerate": True})
    assert code in (200, 201) and a_sum is not None
    print(f"  -> AI Summary generated (version {a_sum['version']})")
    print(f"  {TestColor.OK}[PASS] FLOW 5 PASSED{TestColor.END}\n")
    steps_passed += 1

    # -------------------------------------------------------------------------
    # STEP 6: Arthur Pendelton - Immutable Audit Trail Verification
    # -------------------------------------------------------------------------
    print(f"{TestColor.BOLD}[FLOW 6] Arthur Pendelton: Audit Trail & Provenance Verification...{TestColor.END}")
    code, audit_logs, _ = api_call("GET", f"/patients/{a_id}/audit-logs")
    assert code == 200 and len(audit_logs) >= 3
    actions = [log["action"] for log in audit_logs]
    print(f"  -> Audit Events Logged: {len(audit_logs)} events")
    print(f"  -> Recent Actions: {actions[:4]}")
    assert "TEST_EDITED" in actions
    assert "TESTS_BATCH_VERIFIED" in actions
    print(f"  {TestColor.OK}[PASS] FLOW 6 PASSED{TestColor.END}\n")
    steps_passed += 1

    # -------------------------------------------------------------------------
    # STEP 7: Export Formats (JSON & PDF)
    # -------------------------------------------------------------------------
    print(f"{TestColor.BOLD}[FLOW 7] Multi-Format Export Engine (JSON & PDF)...{TestColor.END}")
    # JSON Export
    code, json_export, _ = api_call("GET", f"/patients/{a_id}/export?format=json")
    assert code == 200 and "metadata" in json_export
    assert json_export["metadata"]["system"] == "MedLens AI-Powered Clinical Intelligence"
    print(f"  -> JSON Export: Validated ({len(json_export['structured_tests'])} tests exported)")

    # PDF Export
    code, pdf_bytes, pdf_headers = api_call("GET", f"/patients/{a_id}/export?format=pdf")
    assert code == 200
    assert "application/pdf" in pdf_headers.get("Content-Type", "")
    assert len(pdf_bytes) > 1000 and pdf_bytes[:5] == b"%PDF-"
    print(f"  -> PDF Clinical Summary Export: Generated {len(pdf_bytes)} bytes of valid PDF binary")
    print(f"  {TestColor.OK}[PASS] FLOW 7 PASSED{TestColor.END}\n")
    steps_passed += 1

    # -------------------------------------------------------------------------
    # STEP 8: Maya Rodriguez & Demo State Reset
    # -------------------------------------------------------------------------
    print(f"{TestColor.BOLD}[FLOW 8] Maya Rodriguez & Demo State Idempotency Reset...{TestColor.END}")
    m_id = maya["id"]
    code, m_intake, _ = api_call("GET", f"/patients/{m_id}/intake")
    assert code == 200 and m_intake["age"] == 34
    print(f"  -> Maya Rodriguez Profile: Intake active (Conditions: {m_intake['existing_conditions']})")

    # Restore Arthur to unverified state for clean UI demo experience
    print("  -> Restoring Arthur Pendelton's tests to unverified status for fresh UI demo...")
    for t in a_tests:
        api_call("PUT", f"/tests/{t['id']}", {"verified": False, "value": original_val if t['id'] == target_test['id'] else t['value']})
    print(f"  {TestColor.OK}[PASS] FLOW 8 PASSED{TestColor.END}\n")
    steps_passed += 1

    # Summary
    print(f"{TestColor.BOLD}========================================================")
    print(f"  ALL {steps_passed}/{total_steps} E2E MOCK FLOWS COMPLETED SUCCESSFULLY")
    print(f"========================================================{TestColor.END}\n")

if __name__ == "__main__":
    try:
        run_e2e_mock()
    except Exception as e:
        print(f"\n{TestColor.FAIL}[ERROR] E2E Mock Runner failed: {e}{TestColor.END}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
