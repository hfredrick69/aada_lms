"""
Tests for /api/progress endpoints (module progress tracking)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date

from app.main import app
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.role import Role
from app.db.models.program import Program, Module
from app.db.models.enrollment import Enrollment, ModuleProgress
from app.core.security import get_password_hash
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


@pytest.fixture
def client(db_session):
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
    alice = User(
        id=uuid.uuid4(),
        email="alice.progress@test.edu",
        password_hash=get_password_hash("TestPass123!"),
        first_name="Alice",
        last_name="Progress"
    )
    instructor = User(
        id=uuid.uuid4(),
        email="instructor.progress@test.edu",
        password_hash=get_password_hash("TestPass123!"),
        first_name="Instructor",
        last_name="Test"
    )
    db_session.add_all([alice, instructor])
    db_session.flush()

    # Create or get roles
    student_role = db_session.query(Role).filter(Role.name == "student").first()
    if not student_role:
        student_role = Role(name="student", description="Student role")
        db_session.add(student_role)
        db_session.flush()

    instructor_role = db_session.query(Role).filter(Role.name == "instructor").first()
    if not instructor_role:
        instructor_role = Role(name="instructor", description="Instructor role")
        db_session.add(instructor_role)
        db_session.flush()

    # Append roles to users
    alice.roles.append(student_role)
    instructor.roles.append(instructor_role)

    db_session.commit()
    db_session.refresh(alice)
    db_session.refresh(instructor)
    return {"alice": alice, "instructor": instructor}


@pytest.fixture
def test_program_and_modules(db_session: Session):
    """Create test program with modules"""
    program = Program(
        id=uuid.uuid4(),
        code="PROG-TEST",
        title="Test Program",
        clock_hours=100
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
            code=f"MOD{i}",
            title=f"Module {i}",
            position=i,
            clock_hours=30
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
    # Return cookies as headers aren't needed - we use cookies
    return {}


# ======================
# GET /api/progress/{user_id}
# ======================

def test_student_can_view_own_progress(
    client: TestClient,
    test_users,
    test_enrollment,
    test_program_and_modules
):
    """Student can view their own overall progress"""
    auth_headers = get_auth_headers(client, "alice.progress@test.edu", "TestPass123!")

    response = client.get(
        f"/api/progress/{test_users['alice'].id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["user_id"] == str(test_users["alice"].id)
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
    test_users,
    test_enrollment,
    test_program_and_modules
):
    """Get module progress when no progress exists (returns default)"""
    auth_headers = get_auth_headers(client, "alice.progress@test.edu", "TestPass123!")

    module_id = test_program_and_modules["modules"][0].id

    response = client.get(
        f"/api/progress/{test_users['alice'].id}/module/{module_id}",
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
    # Create progress record
    module_id = test_program_and_modules["modules"][0].id
    progress = ModuleProgress(
        id=uuid.uuid4(),
        enrollment_id=test_enrollment.id,
        module_id=module_id,
        scorm_status="completed",
        score=95,
        progress_pct=100,
        last_scroll_position=1500,
        active_time_seconds=600,
        sections_viewed=["section-1", "section-2", "section-3"]
    )
    db_session.add(progress)
    db_session.commit()

    auth_headers = get_auth_headers(client, "alice.progress@test.edu", "TestPass123!")

    response = client.get(
        f"/api/progress/{test_users['alice'].id}/module/{module_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["scorm_status"] == "completed"
    assert data["score"] == 95
    assert data["progress_pct"] == 100
    assert data["last_scroll_position"] == 1500
    assert data["active_time_seconds"] == 600
    assert len(data["sections_viewed"]) == 3


# ======================
# POST /api/progress/
# ======================

def test_student_can_update_own_progress(
    client: TestClient,
    test_users,
    test_enrollment,
    test_program_and_modules
):
    """Student can update their own module progress"""
    auth_headers = get_auth_headers(client, "alice.progress@test.edu", "TestPass123!")

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
    test_users,
    test_enrollment,
    test_program_and_modules
):
    """Progress update creates record first time, updates second time"""
    auth_headers = get_auth_headers(client, "alice.progress@test.edu", "TestPass123!")

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
    bob = User(
        id=uuid.uuid4(),
        email="bob.test@test.edu",
        password_hash=get_password_hash("TestPass123!"),
        first_name="Bob",
        last_name="Test",
        roles=["student"]
    )
    db_session.add(bob)
    db_session.commit()
    db_session.refresh(bob)

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
    test_enrollment
):
    """Returns 404 for non-existent module"""
    auth_headers = get_auth_headers(client, "alice.progress@test.edu", "TestPass123!")

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
    test_users,
    test_enrollment,
    test_program_and_modules
):
    """Test complete flow: view, update, view again"""
    auth_headers = get_auth_headers(client, "alice.progress@test.edu", "TestPass123!")

    module_id = test_program_and_modules["modules"][0].id

    # 1. Get initial progress (should be 0%)
    response1 = client.get(
        f"/api/progress/{test_users['alice'].id}",
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
        f"/api/progress/{test_users['alice'].id}",
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
        f"/api/progress/{test_users['alice'].id}/module/{module_id}",
        headers=auth_headers
    )
    assert response4.status_code == 200
    mod_data = response4.json()
    assert mod_data["scorm_status"] == "completed"
    assert mod_data["score"] == 90
