import urllib.request
import json

BASE = "http://127.0.0.1:8000/api"

def test_exports():
    print("[TEST EXPORT] Fetching patients...")
    with urllib.request.urlopen(f"{BASE}/patients") as resp:
        patients = json.loads(resp.read().decode())
    
    assert len(patients) > 0
    for p in patients:
        p_id = p["id"]
        p_name = p["name"]
        print(f"\nTesting export for {p_name} ({p_id})...")

        # 1. JSON Export
        print("  [1] Testing GET /export?format=json...")
        with urllib.request.urlopen(f"{BASE}/patients/{p_id}/export?format=json") as resp:
            assert resp.status == 200
            assert "application/json" in resp.headers.get("Content-Type", "")
            data = json.loads(resp.read().decode())
            assert "metadata" in data
            assert "patient" in data
            assert "structured_tests" in data
            assert "audit_logs" in data
            print(f"      -> JSON OK: {len(data['structured_tests'])} tests, {len(data['audit_logs'])} audit logs")

        # 2. PDF Export
        print("  [2] Testing GET /export?format=pdf...")
        with urllib.request.urlopen(f"{BASE}/patients/{p_id}/export?format=pdf") as resp:
            assert resp.status == 200
            content_type = resp.headers.get("Content-Type", "")
            content_disp = resp.headers.get("Content-Disposition", "")
            assert "application/pdf" in content_type
            assert "attachment" in content_disp
            assert ".pdf" in content_disp
            pdf_bytes = resp.read()
            assert len(pdf_bytes) > 1000
            assert pdf_bytes[:5] == b"%PDF-"
            print(f"      -> PDF OK: Received {len(pdf_bytes)} bytes")
            print(f"      -> Content-Disposition: {content_disp}")

    print("\n[EXPORT TESTS PASSED SUCCESSFULLY!]")

if __name__ == "__main__":
    test_exports()
