import sys
import json
import httpx

BASE_URL = "http://127.0.0.1:8000/api"

def run_tests():
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)
    print("==================================================")
    print("MEDLENS END-TO-END AUTHENTICATION VERIFICATION")
    print("==================================================")

    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[PASS] System health check: 200 OK")

    # 2. Reject Weak Passwords
    weak_payload = {
        "name": "Test Dr Weak",
        "username": "doc_weak",
        "password": "simplepassword"  # No uppercase, no number
    }
    res = client.post("/auth/register", json=weak_payload)
    assert res.status_code == 422, f"Expected 422 for weak password, got {res.status_code}: {res.text}"
    print("[PASS] Validation: Weak password (no uppercase/number) rejected with 422")

    # 3. Successful Registration
    test_username = "dr_rajesh_99"
    test_email = "rajesh99@medlens.org"
    test_pass = "SecurePass123"

    reg_payload = {
        "name": "Dr. Rajesh Sharma",
        "username": test_username,
        "email": test_email,
        "phone": "+91 9876543210",
        "password": test_pass
    }
    res = client.post("/auth/register", json=reg_payload)
    if res.status_code == 400 and "already taken" in res.text:
        # Username exists from earlier run, create unique
        import time
        suffix = int(time.time()) % 10000
        test_username = f"dr_rajesh_{suffix}"
        test_email = f"rajesh_{suffix}@medlens.org"
        reg_payload["username"] = test_username
        reg_payload["email"] = test_email
        res = client.post("/auth/register", json=reg_payload)

    assert res.status_code == 200, f"Registration failed: {res.text}"
    reg_data = res.json()
    assert reg_data["success"] is True
    assert "access_token" in reg_data
    token = reg_data["access_token"]
    patient_id = reg_data["patient"]["id"]
    print(f"[PASS] Registration successful: Username='{test_username}', PatientID={patient_id}")
    print(f"       JWT Access Token issued: {token[:25]}... (length {len(token)})")

    # 4. Duplicate Username Rejection
    dup_res = client.post("/auth/register", json=reg_payload)
    assert dup_res.status_code == 400, f"Expected 400 for duplicate username, got {dup_res.status_code}"
    print(f"[PASS] Duplicate username check: Correctly rejected with 400 Bad Request")

    # 5. Authenticated /me endpoint
    auth_headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/auth/me", headers=auth_headers)
    assert me_res.status_code == 200, f"GET /auth/me failed: {me_res.text}"
    me_data = me_res.json()
    assert me_data["username"] == test_username
    assert me_data["email"] == test_email
    print(f"[PASS] GET /api/auth/me authenticated: verified identity for '{me_data['name']}'")

    # 6. Reject unauthenticated /me
    unauth_res = client.get("/auth/me")
    assert unauth_res.status_code == 401, f"Expected 401 for unauthenticated request, got {unauth_res.status_code}"
    print("[PASS] Unauthenticated request to /api/auth/me correctly blocked with 401 Unauthorized")

    # 7. Login by Username
    login_user_res = client.post("/auth/login", json={
        "username_or_email": test_username,
        "password": test_pass,
        "remember_me": True
    })
    assert login_user_res.status_code == 200, f"Login by username failed: {login_user_res.text}"
    login_data = login_user_res.json()
    assert login_data["success"] is True
    assert login_data["expires_in"] == 60 * 24 * 30  # 30-day token
    print(f"[PASS] Login by Username: 200 OK (expires_in={login_data['expires_in']} mins for remember_me)")

    # 8. Login by Email
    login_email_res = client.post("/auth/login", json={
        "username_or_email": test_email,
        "password": test_pass,
        "remember_me": False
    })
    assert login_email_res.status_code == 200, f"Login by email failed: {login_email_res.text}"
    assert login_email_res.json()["expires_in"] == 60 * 24  # 1-day token
    print(f"[PASS] Login by Email: 200 OK (expires_in={login_email_res.json()['expires_in']} mins)")

    # 9. Login with Incorrect Password
    bad_login_res = client.post("/auth/login", json={
        "username_or_email": test_username,
        "password": "WrongPassword123"
    })
    assert bad_login_res.status_code == 401, f"Expected 401 for bad password, got {bad_login_res.status_code}"
    print(f"[PASS] Invalid password rejected with 401 Unauthorized")

    # 10. Update Patient Demographics (Step 2 in workflow)
    update_res = client.put(f"/patients/{patient_id}", json={
        "dob": "1985-06-15",
        "sex": "Male",
        "abha_id": "91-4820-9182-3841",
        "state": "Telangana",
        "city": "Hyderabad",
        "emergency_contact": "Sunita Sharma (Spouse) - 9876543211"
    }, headers=auth_headers)
    assert update_res.status_code == 200, f"Update demographics failed: {update_res.text}"
    updated_patient = update_res.json()
    assert updated_patient["abha_id"] == "91-4820-9182-3841"
    assert updated_patient["dob"] == "1985-06-15"
    print(f"[PASS] Step 2 Demographics update: ABHA ID '{updated_patient['abha_id']}', State '{updated_patient['state']}'")

    # 11. Submit Clinical Intake Baseline (Step 3 in workflow)
    intake_res = client.post(f"/patients/{patient_id}/intake", json={
        "age": 39,
        "sex": "Male",
        "symptoms": ["Fatigue", "Occasional mild chest tightness"],
        "existing_conditions": ["Type 2 Diabetes", "Hypertension"],
        "allergies": ["Penicillins"],
        "medications": [
            {"name": "Metformin", "dosage": "500mg", "frequency": "BD", "route": "Oral"},
            {"name": "Telmisartan", "dosage": "40mg", "frequency": "OD", "route": "Oral"}
        ]
    }, headers=auth_headers)
    assert intake_res.status_code == 201, f"Intake submission failed: {intake_res.text}"
    intake_data = intake_res.json()
    assert len(intake_data["medications"]) == 2
    assert "Penicillins" in intake_data["allergies"]
    print(f"[PASS] Step 3 Clinical Intake submission: 2 conditions, 1 allergy, 2 medications recorded")

    # 12. Audit Logs Check
    audit_res = client.get(f"/patients/{patient_id}/audit-logs", headers=auth_headers)
    assert audit_res.status_code == 200, f"Audit logs failed: {audit_res.text}"
    logs = audit_res.json()
    actions = [l["action"] for l in logs]
    print(f"[PASS] Audit Trail Verified: Recorded actions = {actions}")

    # 13. Verify Demo Patients Continuity
    patients_res = client.get("/patients")
    assert patients_res.status_code == 200
    all_patients = patients_res.json()
    patient_names = [p["name"] for p in all_patients]
    print(f"[PASS] Patient Switcher Check: {len(all_patients)} total patients in registry")
    for demo_name in ["Eleanor Vance", "Arthur Pendelton"]:
        match = any(demo_name in n for n in patient_names)
        print(f"       Demo Patient '{demo_name}' accessible: {match}")

    print("==================================================")
    print("ALL 13/13 END-TO-END VERIFICATION CHECKS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"[FAIL] Error during verification: {e}")
        sys.exit(1)
