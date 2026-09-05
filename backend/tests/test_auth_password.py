import pytest
from datetime import date
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.db.session import init_db, AsyncSessionLocal
from app.models.patient import Patient
from sqlalchemy import select

@pytest.mark.asyncio
async def test_bcrypt_hashing_and_verification():
    password = "SecurePassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert hashed.startswith("$2b$")
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False

@pytest.mark.asyncio
async def test_jwt_creation_and_decoding():
    payload = {"sub": "patient-test-123", "username": "dr_sharma", "role": "patient"}
    token = create_access_token(payload)
    assert isinstance(token, str)
    decoded = decode_access_token(token)
    assert decoded["sub"] == "patient-test-123"
    assert decoded["username"] == "dr_sharma"

@pytest.mark.asyncio
async def test_patient_model_auth_fields():
    await init_db()
    async with AsyncSessionLocal() as db:
        # Create unique test patient
        uname = "auth_unit_test_user"
        # Clean up if exists
        existing = await db.execute(select(Patient).where(Patient.username == uname))
        found = existing.scalars().first()
        if found:
            await db.delete(found)
            await db.commit()

        p = Patient(
            name="Auth Test User",
            username=uname,
            email="auth_test@medlens.org",
            hashed_password=hash_password("MySecretPass99"),
            phone="+91 9988776655",
            dob=date(1995, 5, 20),
            sex="Male"
        )
        db.add(p)
        await db.commit()
        await db.refresh(p)

        assert p.id is not None
        assert p.username == uname
        assert p.email == "auth_test@medlens.org"
        assert verify_password("MySecretPass99", p.hashed_password) is True

        # Clean up
        await db.delete(p)
        await db.commit()

@pytest.mark.asyncio
async def test_register_and_login_api_flow():
    from httpx import AsyncClient, ASGITransport
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        import uuid
        unique_uname = f"doc_{uuid.uuid4().hex[:8]}"
        unique_email = f"{unique_uname}@medlens.test"
        # 1. Register
        reg_payload = {
            "name": "Dr. Kavitha Rao",
            "username": unique_uname,
            "email": unique_email,
            "phone": "9876501234",
            "password": "SecurePassword123"
        }
        res = await ac.post("/api/auth/register", json=reg_payload)
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["success"] is True
        assert "access_token" in data
        assert data["patient"]["username"] == unique_uname
        token = data["access_token"]

        # 2. Verify duplicate registration fails with 400
        res_dup = await ac.post("/api/auth/register", json=reg_payload)
        assert res_dup.status_code == 400

        # 3. Test Login with Username
        login_res = await ac.post("/api/auth/login", json={
            "username_or_email": unique_uname,
            "password": "SecurePassword123"
        })
        assert login_res.status_code == 200
        login_data = login_res.json()
        assert login_data["success"] is True
        assert "access_token" in login_data
        assert login_data["patient"]["name"] == "Dr. Kavitha Rao"

        # 4. Test Login with Email
        login_email_res = await ac.post("/api/auth/login", json={
            "username_or_email": unique_email,
            "password": "SecurePassword123"
        })
        assert login_email_res.status_code == 200

        # 5. Test Login with Invalid Password
        bad_login = await ac.post("/api/auth/login", json={
            "username_or_email": unique_uname,
            "password": "WrongPassword999"
        })
        assert bad_login.status_code == 401

        # 6. Test GET /api/auth/me with Bearer token
        me_res = await ac.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert me_data["authenticated"] is True
        assert me_data["patient"]["username"] == unique_uname

