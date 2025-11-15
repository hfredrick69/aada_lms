"""Tests for Enrollment endpoints"""
from uuid import uuid4
from datetime import date, timedelta
from fastapi.testclient import TestClient

from app.db.models.program import Program
from app.db.session import SessionLocal
from app.main import app
from app.tests.utils import create_user_with_roles

client = TestClient(app)


def _create_user(email: str, password: str, roles: list[str] | None = None):
    """Helper to create user with roles"""
    session = SessionLocal()
    try:
        user = create_user_with_roles(session, email=email, password=password, roles=roles)
        session.expunge_all()
        return user
    finally:
        session.close()


def _create_program():
    """Helper to create program"""
    session = SessionLocal()
    try:
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
        return program
    finally:
        session.close()


def _get_auth_token(email: str, password: str):
    """Helper to get JWT token"""
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_admin_can_create_enrollment():
    """Test admin can create enrollment"""
    admin_email = "enroll.admin@test.edu"
    student_email = "enroll.student@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    student = _create_user(student_email, password, roles=["student"])
    program = _create_program()
    token = _get_auth_token(admin_email, password)

    enrollment_data = {
        "user_id": str(student.id),
        "program_id": str(program.id),
        "start_date": str(date.today()),
        "expected_end_date": str(date.today() + timedelta(days=365)),
        "status": "active"
    }

    response = client.post(
        "/api/enrollments",
        json=enrollment_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == str(student.id)
    assert data["program_id"] == str(program.id)
    assert data["status"] == "active"


def test_student_cannot_create_enrollment():
    """Test students cannot create enrollments"""
    student_email = "enroll.nostudent@test.edu"
    password = "StudentPass!23"

    student = _create_user(student_email, password, roles=["student"])
    program = _create_program()
    token = _get_auth_token(student_email, password)

    enrollment_data = {
        "user_id": str(student.id),
        "program_id": str(program.id),
        "start_date": str(date.today())
    }

    response = client.post(
        "/api/enrollments",
        json=enrollment_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_admin_can_update_enrollment():
    """Test admin can update enrollment"""
    admin_email = "enroll.update.admin@test.edu"
    student_email = "enroll.update.student@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    student = _create_user(student_email, password, roles=["student"])
    program = _create_program()
    token = _get_auth_token(admin_email, password)

    # Create enrollment first
    enrollment_data = {
        "user_id": str(student.id),
        "program_id": str(program.id),
        "start_date": str(date.today()),
        "status": "active"
    }

    create_response = client.post(
        "/api/enrollments",
        json=enrollment_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 201
    enrollment_id = create_response.json()["id"]

    # Update enrollment
    update_data = {
        "status": "completed",
        "expected_end_date": str(date.today() + timedelta(days=180))
    }

    response = client.put(
        f"/api/enrollments/{enrollment_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["expected_end_date"] is not None


def test_student_cannot_update_enrollment():
    """Test students cannot update enrollments"""
    admin_email = "enroll.noupdate.admin@test.edu"
    student_email = "enroll.noupdate.student@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    student = _create_user(student_email, password, roles=["student"])
    program = _create_program()
    admin_token = _get_auth_token(admin_email, password)
    student_token = _get_auth_token(student_email, password)

    # Admin creates enrollment
    enrollment_data = {
        "user_id": str(student.id),
        "program_id": str(program.id),
        "start_date": str(date.today())
    }

    create_response = client.post(
        "/api/enrollments",
        json=enrollment_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert create_response.status_code == 201
    enrollment_id = create_response.json()["id"]

    # Student tries to update
    update_data = {"status": "completed"}
    response = client.put(
        f"/api/enrollments/{enrollment_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == 403


def test_student_can_view_own_enrollments():
    """Test student can view their own enrollments"""
    admin_email = "enroll.view.admin@test.edu"
    student_email = "enroll.view.student@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    student = _create_user(student_email, password, roles=["student"])
    program = _create_program()
    admin_token = _get_auth_token(admin_email, password)
    student_token = _get_auth_token(student_email, password)

    # Admin creates enrollment for student
    enrollment_data = {
        "user_id": str(student.id),
        "program_id": str(program.id),
        "start_date": str(date.today())
    }

    create_response = client.post(
        "/api/enrollments",
        json=enrollment_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert create_response.status_code == 201

    # Student views their enrollments
    response = client.get(
        "/api/enrollments",
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(enrollment["user_id"] == str(student.id) for enrollment in data)


def test_admin_can_view_all_enrollments():
    """Test admin can view all enrollments"""
    admin_email = "enroll.viewall.admin@test.edu"
    student1_email = "enroll.viewall.student1@test.edu"
    student2_email = "enroll.viewall.student2@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    student1 = _create_user(student1_email, password, roles=["student"])
    student2 = _create_user(student2_email, password, roles=["student"])
    program = _create_program()
    token = _get_auth_token(admin_email, password)

    # Create enrollments for both students
    for student in [student1, student2]:
        enrollment_data = {
            "user_id": str(student.id),
            "program_id": str(program.id),
            "start_date": str(date.today())
        }
        client.post(
            "/api/enrollments",
            json=enrollment_data,
            headers={"Authorization": f"Bearer {token}"}
        )

    # Admin views all enrollments
    response = client.get(
        "/api/enrollments",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_admin_can_delete_enrollment():
    """Test admin can delete enrollment"""
    admin_email = "enroll.delete.admin@test.edu"
    student_email = "enroll.delete.student@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    student = _create_user(student_email, password, roles=["student"])
    program = _create_program()
    token = _get_auth_token(admin_email, password)

    # Create enrollment
    enrollment_data = {
        "user_id": str(student.id),
        "program_id": str(program.id),
        "start_date": str(date.today())
    }

    create_response = client.post(
        "/api/enrollments",
        json=enrollment_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    enrollment_id = create_response.json()["id"]

    # Delete enrollment
    response = client.delete(
        f"/api/enrollments/{enrollment_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(
        f"/api/enrollments/{enrollment_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404


def test_student_cannot_delete_enrollment():
    """Test student cannot delete enrollment"""
    admin_email = "enroll.nodelete.admin@test.edu"
    student_email = "enroll.nodelete.student@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    student = _create_user(student_email, password, roles=["student"])
    program = _create_program()
    admin_token = _get_auth_token(admin_email, password)
    student_token = _get_auth_token(student_email, password)

    # Admin creates enrollment
    enrollment_data = {
        "user_id": str(student.id),
        "program_id": str(program.id),
        "start_date": str(date.today())
    }

    create_response = client.post(
        "/api/enrollments",
        json=enrollment_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert create_response.status_code == 201
    enrollment_id = create_response.json()["id"]

    # Student tries to delete
    response = client.delete(
        f"/api/enrollments/{enrollment_id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == 403


def test_get_enrollment_404():
    """Test 404 when enrollment doesn't exist"""
    admin_email = "enroll.404@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    token = _get_auth_token(admin_email, password)

    fake_id = uuid4()
    response = client.get(
        f"/api/enrollments/{fake_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
