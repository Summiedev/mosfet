"""
Basic test suite for RadFlow API.
Run with:  pytest tests/ -v

Requires a running MongoDB instance (uses a separate test DB).
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Force test DB before importing app
os.environ["MONGODB_DB_NAME"] = "radflow_test"
os.environ["APP_ENV"] = "development"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

from app.main import app
from app.core.database import connect_db, close_db, get_db


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    await connect_db()
    yield
    # Clean test DB after all tests
    db = get_db()
    client = db.client
    await client.drop_database("radflow_test")
    await close_db()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers(client):
    """Register + login, return auth headers."""
    await client.post("/api/v1/auth/register", json={
        "full_name": "Test Radiologist",
        "email": "test@radflow.com",
        "phone": "+2348099999999",
        "password": "testpass123",
        "role": "hybrid",
    })
    login = await client.post("/api/v1/auth/login", json={
        "email": "test@radflow.com",
        "password": "testpass123",
    })
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ── Auth tests ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register(client):
    resp = await client.post("/api/v1/auth/register", json={
        "full_name": "New User",
        "email": "new@radflow.com",
        "phone": "+2348011111111",
        "password": "password123",
        "role": "hybrid",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["role"] == "hybrid"


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {
        "full_name": "Duplicate",
        "email": "dup@radflow.com",
        "phone": "+2348022222222",
        "password": "password123",
        "role": "hybrid",
    }
    await client.post("/api/v1/auth/register", json=payload)
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/v1/auth/register", json={
        "full_name": "Wrong Pass",
        "email": "wrongpass@radflow.com",
        "phone": "+2348033333333",
        "password": "correctpass",
        "role": "hybrid",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "wrongpass@radflow.com",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client, auth_headers):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@radflow.com"


# ── Patient tests ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_patient(client, auth_headers):
    resp = await client.post("/api/v1/patients", json={
        "name": "Test Patient",
        "age": 35,
        "sex": "female",
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["name"] == "Test Patient"


@pytest.mark.asyncio
async def test_get_patient(client, auth_headers):
    create = await client.post("/api/v1/patients", json={
        "name": "Fetch Me",
        "age": 30,
    }, headers=auth_headers)
    patient_id = create.json()["id"]

    resp = await client.get(f"/api/v1/patients/{patient_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Fetch Me"


# ── Scan tests ────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def scan_setup(client, auth_headers):
    """Create a patient + scan session for scan tests."""
    patient = await client.post("/api/v1/patients", json={
        "name": "Scan Test Patient",
        "age": 40,
        "sex": "female",
    }, headers=auth_headers)
    patient_id = patient.json()["id"]

    scan = await client.post("/api/v1/scans", json={
        "patient_id": patient_id,
        "scan_type": "breast_ultrasound",
        "clinical_indication": "Palpable lump — screening",
    }, headers=auth_headers)
    return {"patient_id": patient_id, "scan": scan.json()}


@pytest.mark.asyncio
async def test_create_scan(scan_setup):
    scan = scan_setup["scan"]
    assert scan["status"] == "pending"
    assert scan["scan_type"] == "breast_ultrasound"
    assert len(scan["checklist"]) > 0


@pytest.mark.asyncio
async def test_update_scan(client, auth_headers, scan_setup):
    scan_id = scan_setup["scan"]["id"]
    resp = await client.patch(f"/api/v1/scans/{scan_id}", json={
        "transcript": "Hypoechoic mass noted in upper outer quadrant.",
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert "Hypoechoic" in resp.json()["transcript"]


@pytest.mark.asyncio
async def test_get_ai_events(client, auth_headers, scan_setup):
    scan_id = scan_setup["scan"]["id"]
    resp = await client.get(
        f"/api/v1/scans/{scan_id}/ai-events?elapsed=20",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    events = resp.json()["events"]
    # Only events at or before t=20 should be returned
    assert all(e["timestamp_seconds"] <= 20 for e in events)


@pytest.mark.asyncio
async def test_validate_scan_incomplete(client, auth_headers, scan_setup):
    scan_id = scan_setup["scan"]["id"]
    resp = await client.post(f"/api/v1/scans/{scan_id}/validate", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["valid"] is False
    assert len(resp.json()["missing_fields"]) > 0


@pytest.mark.asyncio
async def test_dashboard(client, auth_headers):
    resp = await client.get("/api/v1/dashboard", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "pending_scans" in data
    assert "recent_completed" in data
    assert "total_today" in data


# ── Checklist tests ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_checklist(client, auth_headers):
    resp = await client.get("/api/v1/checklists/breast_ultrasound", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["scan_type"] == "breast_ultrasound"
    assert len(resp.json()["items"]) > 0


@pytest.mark.asyncio
async def test_get_checklist_invalid(client, auth_headers):
    resp = await client.get("/api/v1/checklists/invalid_type", headers=auth_headers)
    assert resp.status_code == 404


# ── Health check ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
