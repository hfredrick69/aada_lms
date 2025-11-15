"""Tests for SCORM tracking endpoints"""
from uuid import uuid4
from fastapi.testclient import TestClient

from app.db.models.program import Program, Module
from app.db.session import SessionLocal
from app.main import app
from app.tests.utils import create_user_with_roles

client = TestClient(app)


def _create_user(email: str, password: str, roles: list[str] | None = None):
    """Helper to create user with roles"""
    session = SessionLocal()
    try:
        return create_user_with_roles(session, email=email, password=password, roles=roles)
    finally:
        session.close()


def _create_module():
    """Helper to create program and module"""
    session = SessionLocal()
    try:
        # Use unique codes to avoid conflicts between tests
        unique_id = str(uuid4())[:8]
        program = Program(
            code=f"TEST-PROG-{unique_id}",
            name="Test Program",
            credential_level="certificate",
            total_clock_hours=100
        )
        session.add(program)
        session.commit()
        session.refresh(program)

        module = Module(
            program_id=program.id,
            code=f"TEST-MOD-{unique_id}",
            title="Test Module",
            delivery_type="online",
            clock_hours=10,
            position=1
        )
        session.add(module)
        session.commit()
        session.refresh(module)
        return module
    finally:
        session.close()


def _get_auth_token(email: str, password: str):
    """Helper to get JWT token"""
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_create_scorm_record_as_student():
    """Test student can create SCORM record for their own module"""
    email = "scorm.student@test.edu"
    password = "StudentPass!23"
    user = _create_user(email, password, roles=["student"])
    module = _create_module()
    token = _get_auth_token(email, password)

    scorm_data = {
        "user_id": str(user.id),
        "module_id": str(module.id),
        "lesson_status": "completed",
        "score_scaled": 0.95,
        "score_raw": 95.0,
        "session_time": "00:15:30",
        "interactions": {"q1": "answer1", "q2": "answer2"}
    }

    response = client.post(
        "/api/scorm/records",
        json=scorm_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == str(user.id)
    assert data["module_id"] == str(module.id)
    assert data["lesson_status"] == "completed"
    assert float(data["score_scaled"]) == 0.95
    assert data["interactions"] == {"q1": "answer1", "q2": "answer2"}


def test_update_existing_scorm_record():
    """Test updating existing SCORM record (upsert functionality)"""
    email = "scorm.update@test.edu"
    password = "StudentPass!23"
    user = _create_user(email, password, roles=["student"])
    module = _create_module()
    token = _get_auth_token(email, password)

    # Create initial record
    initial_data = {
        "user_id": str(user.id),
        "module_id": str(module.id),
        "lesson_status": "incomplete",
        "score_raw": 50.0
    }
    response = client.post(
        "/api/scorm/records",
        json=initial_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201

    # Update with better score
    updated_data = {
        "user_id": str(user.id),
        "module_id": str(module.id),
        "lesson_status": "passed",
        "score_raw": 95.0,
        "score_scaled": 0.95
    }
    response = client.post(
        "/api/scorm/records",
        json=updated_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["lesson_status"] == "passed"
    assert float(data["score_raw"]) == 95.0
    assert float(data["score_scaled"]) == 0.95


def test_student_cannot_update_other_student_record():
    """Test students cannot update other students' SCORM records"""
    student1_email = "student1@test.edu"
    student2_email = "student2@test.edu"
    password = "StudentPass!23"

    student1 = _create_user(student1_email, password, roles=["student"])
    _create_user(student2_email, password, roles=["student"])
    module = _create_module()

    scorm_data = {
        "user_id": str(student1.id),
        "module_id": str(module.id),
        "lesson_status": "completed"
    }

    # Try to update as student2
    token2 = _get_auth_token(student2_email, password)
    response = client.post(
        "/api/scorm/records",
        json=scorm_data,
        headers={"Authorization": f"Bearer {token2}"}
    )

    assert response.status_code == 403


def test_get_scorm_record_for_resume():
    """Test retrieving SCORM record for resume functionality"""
    email = "scorm.resume@test.edu"
    password = "StudentPass!23"
    user = _create_user(email, password, roles=["student"])
    module = _create_module()
    token = _get_auth_token(email, password)

    # Create SCORM record
    scorm_data = {
        "user_id": str(user.id),
        "module_id": str(module.id),
        "lesson_status": "incomplete",
        "score_raw": 75.0,
        "session_time": "00:30:00"
    }
    client.post(
        "/api/scorm/records",
        json=scorm_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Retrieve for resume
    response = client.get(
        f"/api/scorm/records/{user.id}/{module.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["lesson_status"] == "incomplete"
    assert float(data["score_raw"]) == 75.0
    assert data["session_time"] == "00:30:00"


def test_get_nonexistent_scorm_record():
    """Test 404 when SCORM record doesn't exist"""
    email = "scorm.notfound@test.edu"
    password = "StudentPass!23"
    user = _create_user(email, password, roles=["student"])
    module = _create_module()
    token = _get_auth_token(email, password)

    response = client.get(
        f"/api/scorm/records/{user.id}/{module.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404


def test_list_all_user_scorm_records():
    """Test listing all SCORM records for a user"""
    email = "scorm.list@test.edu"
    password = "StudentPass!23"
    user = _create_user(email, password, roles=["student"])
    module1 = _create_module()
    module2 = _create_module()
    token = _get_auth_token(email, password)

    # Create records for two modules
    for module in [module1, module2]:
        scorm_data = {
            "user_id": str(user.id),
            "module_id": str(module.id),
            "lesson_status": "completed",
            "score_raw": 90.0
        }
        client.post(
            "/api/scorm/records",
            json=scorm_data,
            headers={"Authorization": f"Bearer {token}"}
        )

    # List all records
    response = client.get(
        f"/api/scorm/records/{user.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(record["user_id"] == str(user.id) for record in data)


def test_instructor_can_delete_scorm_record():
    """Test instructor can delete SCORM records"""
    student_email = "scorm.delete.student@test.edu"
    instructor_email = "scorm.delete.instructor@test.edu"
    password = "TestPass!234"

    student = _create_user(student_email, password, roles=["student"])
    _create_user(instructor_email, password, roles=["instructor"])
    module = _create_module()
    student_token = _get_auth_token(student_email, password)
    instructor_token = _get_auth_token(instructor_email, password)

    # Student creates record
    scorm_data = {
        "user_id": str(student.id),
        "module_id": str(module.id),
        "lesson_status": "completed"
    }
    client.post(
        "/api/scorm/records",
        json=scorm_data,
        headers={"Authorization": f"Bearer {student_token}"}
    )

    # Instructor deletes record
    response = client.delete(
        f"/api/scorm/records/{student.id}/{module.id}",
        headers={"Authorization": f"Bearer {instructor_token}"}
    )

    assert response.status_code == 204

    # Verify it's deleted
    response = client.get(
        f"/api/scorm/records/{student.id}/{module.id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 404


def test_student_cannot_delete_scorm_record():
    """Test students cannot delete SCORM records"""
    email = "scorm.nodelete@test.edu"
    password = "StudentPass!23"
    user = _create_user(email, password, roles=["student"])
    module = _create_module()
    token = _get_auth_token(email, password)

    # Create record
    scorm_data = {
        "user_id": str(user.id),
        "module_id": str(module.id),
        "lesson_status": "completed"
    }
    client.post(
        "/api/scorm/records",
        json=scorm_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Try to delete
    response = client.delete(
        f"/api/scorm/records/{user.id}/{module.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
