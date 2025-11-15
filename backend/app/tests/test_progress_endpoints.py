"""
Tests for /api/progress endpoints (module progress tracking)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date

from app.main import app
from app.db.session import get_db
from app.db.models.program import Program, Module
from app.db.models.enrollment import Enrollment, ModuleProgress
from app.tests.utils import create_user_with_roles
import uuid


@pytest.fixture
def db_session():
    """Create a test database session"""
    from app.db.base import Base
    from app.db.session import engine
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    yield db
    db.close()


@pytest.fixture(name="client")
def client_fixture(db_session):
    """Create test client"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_users(db_session: Session):
    """Create test users"""
    alice = create_user_with_roles(
        db_session,
        email="alice.progress@test.edu",
        password="TestPass123!",
        first_name="Alice",
        last_name="Progress",
        roles=["student"],
    )
    instructor = create_user_with_roles(
        db_session,
        email="instructor.progress@test.edu",
        password="TestPass123!",
        first_name="Instructor",
        last_name="Test",
        roles=["instructor"],
    )
    return {"alice": alice, "instructor": instructor}


@pytest.fixture
def test_program_and_modules(db_session: Session):
    """Create test program with modules"""
    program_code = f"PROG-{uuid.uuid4().hex[:6]}"
    program = Program(
        id=uuid.uuid4(),
        code=program_code,
        name="Test Program",
        credential_level="certificate",
        total_clock_hours=100,
    )
    db_session.add(program)
    db_session.commit()
    db_session.refresh(program)

    # Create 3 modules
    modules = []
    for i in range(1, 4):
        module = Module(
            id=uuid.uuid4(),
            program_id=program.id,
            code=f"{program_code}-MOD{i}",
            title=f"Module {i}",
            delivery_type="online",
            clock_hours=30,
            requires_in_person=False,
            position=i,
        )
        modules.append(module)

    db_session.add_all(modules)
    db_session.commit()
    for mod in modules:
        db_session.refresh(mod)

    return {"program": program, "modules": modules}


@pytest.fixture
def test_enrollment(db_session: Session, test_users, test_program_and_modules):
    """Create test enrollment"""
    enrollment = Enrollment(
        id=uuid.uuid4(),
        user_id=test_users["alice"].id,
        program_id=test_program_and_modules["program"].id,
        start_date=date.today(),
        status="active"
    )
    db_session.add(enrollment)
    db_session.commit()
    db_session.refresh(enrollment)
    return enrollment


def get_auth_headers(client: TestClient, email: str, password: str):
    """Get authentication headers"""
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    data = response.json()
    token = data.get("access_token")
    assert token, "Login response missing access_token"
    return {"Authorization": f"Bearer {token}"}


def get_current_user_id(client: TestClient, headers: dict) -> str:
    me_response = client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == 200, me_response.text
    return me_response.json()["id"]


def align_enrollment_owner(db_session: Session, enrollment: Enrollment, current_user_id: str):
    owner_id = uuid.UUID(current_user_id)
    if enrollment.user_id != owner_id:
        enrollment.user_id = owner_id
        db_session.add(enrollment)
    db_session.query(Enrollment).filter(
        Enrollment.user_id == owner_id,
        Enrollment.id != enrollment.id
    ).delete(synchronize_session=False)
    db_session.query(ModuleProgress).filter(
        ModuleProgress.enrollment_id == enrollment.id
    ).delete(synchronize_session=False)
    db_session.commit()


def login_and_prepare_student(
    client: TestClient,
    db_session: Session,
    enrollment: Enrollment,
    email: str = "alice.progress@test.edu",
    password: str = "TestPass123!"
):
    headers = get_auth_headers(client, email, password)
    current_user_id = get_current_user_id(client, headers)
    align_enrollment_owner(db_session, enrollment, current_user_id)
    return headers, current_user_id


# ======================
# GET /api/progress/{user_id}
# ======================

def test_student_can_view_own_progress(
    client: TestClient,
    db_session: Session,
    test_users,
    test_enrollment,
    test_program_and_modules
):
    """Student can view their own overall progress"""
    auth_headers, current_user_id = login_and_prepare_student(client, db_session, test_enrollment)

    response = client.get(
        f"/api/progress/{current_user_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["user_id"] == str(current_user_id)
    assert data["enrollment_id"] == str(test_enrollment.id)
    assert data["total_modules"] == 3
    assert data["completed_modules"] == 0
    assert data["completion_percentage"] == 0.0
    assert len(data["modules"]) == 3


def test_student_cannot_view_other_progress(
    client: TestClient,
    test_users,
    test_enrollment
):
    """Student cannot view another student's progress"""
    auth_headers = get_auth_headers(client, "alice.progress@test.edu", "TestPass123!")

    # Try to access instructor's progress
    response = client.get(
        f"/api/progress/{test_users['instructor'].id}",
        headers=auth_headers
    )

    assert response.status_code == 403


def test_instructor_can_view_student_progress(
    client: TestClient,
    test_users,
    test_enrollment,
    test_program_and_modules
):
    """Instructor can view student progress"""
    auth_headers = get_auth_headers(client, "instructor.progress@test.edu", "TestPass123!")

    response = client.get(
        f"/api/progress/{test_users['alice'].id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(test_users["alice"].id)


def test_progress_404_no_enrollment(
    client: TestClient,
    test_users
):
    """Returns 404 when user has no active enrollment"""
    auth_headers = get_auth_headers(client, "instructor.progress@test.edu", "TestPass123!")

    response = client.get(
        f"/api/progress/{test_users['instructor'].id}",
        headers=auth_headers
    )

    assert response.status_code == 404
    assert "No active enrollment found" in response.json()["detail"]


# ======================
# GET /api/progress/{user_id}/module/{module_id}
# ======================

def test_get_module_progress_no_progress_record(
    client: TestClient,
    db_session: Session,
    test_users,
    test_enrollment,
    test_program_and_modules
):
    """Get module progress when no progress exists (returns default)"""
    auth_headers, current_user_id = login_and_prepare_student(client, db_session, test_enrollment)

    module_id = test_program_and_modules["modules"][0].id

    response = client.get(
        f"/api/progress/{current_user_id}/module/{module_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["module_id"] == str(module_id)
    assert data["scorm_status"] == "incomplete"
    assert data["progress_pct"] == 0
    assert data["last_scroll_position"] == 0
    assert data["active_time_seconds"] == 0
    assert data["sections_viewed"] == []


def test_get_module_progress_with_existing_progress(
    client: TestClient,
    db_session: Session,
    test_users,
    test_enrollment,
    test_program_and_modules
):
    """Get module progress when progress record exists"""
    module_id = test_program_and_modules["modules"][0].id

    auth_headers, current_user_id = login_and_prepare_student(client, db_session, test_enrollment)

    progress_payload = {
        "enrollment_id": str(test_enrollment.id),
        "module_id": str(module_id),
        "scorm_status": "completed",
        "score": 95,
        "progress_pct": 100,
        "last_scroll_position": 1500,
        "active_time_seconds": 600,
        "sections_viewed": ["section-1", "section-2", "section-3"],
    }
    assert current_user_id == str(test_enrollment.user_id)
    create_resp = client.post("/api/progress/", json=progress_payload, headers=auth_headers)
    assert create_resp.status_code == 201, create_resp.text

    response = client.get(
        f"/api/progress/{current_user_id}/module/{module_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["scorm_status"] == "completed"
    assert data["score"] == 95
    assert data["progress_pct"] == 100
    assert data["last_scroll_position"] == 1500
    assert data["active_time_seconds"] == 600
    assert data["sections_viewed"] == ["section-1", "section-2", "section-3"]


# ======================
# POST /api/progress/
# ======================

def test_student_can_update_own_progress(
    client: TestClient,
    db_session: Session,
    test_users,
    test_enrollment,
    test_program_and_modules
):
    """Student can update their own module progress"""
    auth_headers = get_auth_headers(client, "alice.progress@test.edu", "TestPass123!")

    current_user_id = get_current_user_id(client, auth_headers)
    align_enrollment_owner(db_session, test_enrollment, current_user_id)

    module_id = test_program_and_modules["modules"][0].id

    progress_data = {
        "enrollment_id": str(test_enrollment.id),
        "module_id": str(module_id),
        "scorm_status": "incomplete",
        "progress_pct": 50,
        "last_scroll_position": 800,
        "active_time_seconds": 300,
        "sections_viewed": ["intro", "section-1"]
    }

    response = client.post(
        "/api/progress/",
        json=progress_data,
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()

    assert data["scorm_status"] == "incomplete"
    assert data["progress_pct"] == 50
    assert data["last_scroll_position"] == 800
    assert data["active_time_seconds"] == 300
    assert len(data["sections_viewed"]) == 2


def test_update_progress_creates_then_updates(
    client: TestClient,
    db_session: Session,
    test_users,
    test_enrollment,
    test_program_and_modules
):
    """Progress update creates record first time, updates second time"""
    auth_headers, current_user_id = login_and_prepare_student(client, db_session, test_enrollment)

    module_id = test_program_and_modules["modules"][0].id

    # First update - creates record
    progress_data = {
        "enrollment_id": str(test_enrollment.id),
        "module_id": str(module_id),
        "progress_pct": 25,
        "active_time_seconds": 100
    }

    response1 = client.post("/api/progress/", json=progress_data, headers=auth_headers)
    assert response1.status_code == 201
    progress_id = response1.json()["id"]

    # Second update - updates same record
    progress_data["progress_pct"] = 75
    progress_data["active_time_seconds"] = 500

    response2 = client.post("/api/progress/", json=progress_data, headers=auth_headers)
    assert response2.status_code == 201

    # Should be same ID
    assert response2.json()["id"] == progress_id
    assert response2.json()["progress_pct"] == 75
    assert response2.json()["active_time_seconds"] == 500


def test_student_cannot_update_other_enrollment_progress(
    client: TestClient,
    db_session: Session,
    test_users,
    test_enrollment,
    test_program_and_modules
):
    """Student cannot update progress for another student's enrollment"""
    # Create another user and enrollment
    bob = create_user_with_roles(
        db_session,
        email="bob.test@test.edu",
        password="TestPass123!",
        first_name="Bob",
        last_name="Test",
        roles=["student"],
    )

    bob_enrollment = Enrollment(
        id=uuid.uuid4(),
        user_id=bob.id,
        program_id=test_program_and_modules["program"].id,
        start_date=date.today(),
        status="active"
    )
    db_session.add(bob_enrollment)
    db_session.commit()

    # Alice tries to update Bob's progress
    auth_headers = get_auth_headers(client, "alice.progress@test.edu", "TestPass123!")

    progress_data = {
        "enrollment_id": str(bob_enrollment.id),
        "module_id": str(test_program_and_modules["modules"][0].id),
        "progress_pct": 100
    }

    response = client.post("/api/progress/", json=progress_data, headers=auth_headers)
    assert response.status_code == 403


def test_instructor_can_update_student_progress(
    client: TestClient,
    test_enrollment,
    test_program_and_modules
):
    """Instructor can update student progress"""
    auth_headers = get_auth_headers(client, "instructor.progress@test.edu", "TestPass123!")

    progress_data = {
        "enrollment_id": str(test_enrollment.id),
        "module_id": str(test_program_and_modules["modules"][0].id),
        "scorm_status": "passed",
        "score": 100,
        "progress_pct": 100
    }

    response = client.post("/api/progress/", json=progress_data, headers=auth_headers)
    assert response.status_code == 201

    data = response.json()
    assert data["scorm_status"] == "passed"
    assert data["score"] == 100


def test_update_progress_404_invalid_enrollment(
    client: TestClient,
    test_program_and_modules
):
    """Returns 404 for non-existent enrollment"""
    auth_headers = get_auth_headers(client, "alice.progress@test.edu", "TestPass123!")

    progress_data = {
        "enrollment_id": str(uuid.uuid4()),  # Random UUID
        "module_id": str(test_program_and_modules["modules"][0].id),
        "progress_pct": 50
    }

    response = client.post("/api/progress/", json=progress_data, headers=auth_headers)
    assert response.status_code == 404


def test_update_progress_404_invalid_module(
    client: TestClient,
    db_session: Session,
    test_enrollment
):
    """Returns 404 for non-existent module"""
    auth_headers, _ = login_and_prepare_student(client, db_session, test_enrollment)

    progress_data = {
        "enrollment_id": str(test_enrollment.id),
        "module_id": str(uuid.uuid4()),  # Random UUID
        "progress_pct": 50
    }

    response = client.post("/api/progress/", json=progress_data, headers=auth_headers)
    assert response.status_code == 404


# ======================
# Integration Tests
# ======================

def test_complete_progress_tracking_flow(
    client: TestClient,
    db_session: Session,
    test_users,
    test_enrollment,
    test_program_and_modules
):
    """Test complete flow: view, update, view again"""
    auth_headers, current_user_id = login_and_prepare_student(client, db_session, test_enrollment)

    module_id = test_program_and_modules["modules"][0].id

    # 1. Get initial progress (should be 0%)
    response1 = client.get(
        f"/api/progress/{current_user_id}",
        headers=auth_headers
    )
    assert response1.status_code == 200
    assert response1.json()["completion_percentage"] == 0.0

    # 2. Update progress for module 1
    progress_data = {
        "enrollment_id": str(test_enrollment.id),
        "module_id": str(module_id),
        "scorm_status": "completed",
        "score": 90,
        "progress_pct": 100
    }

    response2 = client.post("/api/progress/", json=progress_data, headers=auth_headers)
    assert response2.status_code == 201

    # 3. Get updated overall progress
    response3 = client.get(
        f"/api/progress/{current_user_id}",
        headers=auth_headers
    )
    assert response3.status_code == 200
    data = response3.json()

    # Should show 1 of 3 modules completed (33.33%)
    assert data["completed_modules"] == 1
    assert data["completion_percentage"] > 33.0
    assert data["completion_percentage"] < 34.0

    # 4. Get specific module progress
    response4 = client.get(
        f"/api/progress/{current_user_id}/module/{module_id}",
        headers=auth_headers
    )
    assert response4.status_code == 200
    mod_data = response4.json()
    assert mod_data["scorm_status"] == "completed"
    assert mod_data["score"] == 90
