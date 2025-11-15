"""Tests for Student endpoints"""
from uuid import uuid4
from fastapi.testclient import TestClient

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


def _get_auth_token(email: str, password: str):
    """Helper to get JWT token"""
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_admin_can_list_students():
    """Test admin can list all students"""
    admin_email = "students.list.admin@test.edu"
    student_email = "students.list.student@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(admin_email, password)

    response = client.get(
        "/api/students/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_staff_can_list_students():
    """Test staff can list all students"""
    staff_email = "students.liststaff.staff@test.edu"
    student_email = "students.liststaff.student@test.edu"
    password = "StaffPass!234"

    _create_user(staff_email, password, roles=["staff"])
    _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(staff_email, password)

    response = client.get(
        "/api/students/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_student_cannot_list_students():
    """Test student cannot list students"""
    student_email = "students.nolist.student@test.edu"
    password = "StudentPass!234"

    _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(student_email, password)

    response = client.get(
        "/api/students/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_admin_can_create_student():
    """Test admin can create new student"""
    admin_email = "students.create.admin@test.edu"
    new_student_email = f"student.{uuid4()}@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    token = _get_auth_token(admin_email, password)

    student_data = {
        "email": new_student_email,
        "password": "NewStudentPass!234",
        "first_name": "New",
        "last_name": "Student"
    }

    response = client.post(
        "/api/students/",
        json=student_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == new_student_email
    assert data["first_name"] == "New"
    assert data["last_name"] == "Student"


def test_staff_can_create_student():
    """Test staff can create new student"""
    staff_email = "students.createstaff.staff@test.edu"
    new_student_email = f"student.{uuid4()}@test.edu"
    password = "StaffPass!234"

    _create_user(staff_email, password, roles=["staff"])
    token = _get_auth_token(staff_email, password)

    student_data = {
        "email": new_student_email,
        "password": "NewStudentPass!234",
        "first_name": "New",
        "last_name": "Student"
    }

    response = client.post(
        "/api/students/",
        json=student_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201


def test_student_cannot_create_student():
    """Test students cannot create students"""
    student_email = "students.nocreate.student@test.edu"
    new_student_email = f"student.{uuid4()}@test.edu"
    password = "StudentPass!234"

    _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(student_email, password)

    student_data = {
        "email": new_student_email,
        "password": "NewStudentPass!234",
        "first_name": "New",
        "last_name": "Student"
    }

    response = client.post(
        "/api/students/",
        json=student_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_cannot_create_duplicate_email():
    """Test cannot create student with duplicate email"""
    admin_email = "students.dup.admin@test.edu"
    duplicate_email = "students.duplicate@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    _create_user(duplicate_email, password, roles=["student"])
    token = _get_auth_token(admin_email, password)

    student_data = {
        "email": duplicate_email,
        "password": "NewStudentPass!234",
        "first_name": "Duplicate",
        "last_name": "Student"
    }

    response = client.post(
        "/api/students/",
        json=student_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_admin_can_get_student():
    """Test admin can get any student by ID"""
    admin_email = "students.get.admin@test.edu"
    student_email = "students.get.student@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    student = _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(admin_email, password)

    response = client.get(
        f"/api/students/{student.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == student_email


def test_staff_can_get_student():
    """Test staff can get any student by ID"""
    staff_email = "students.getstaff.staff@test.edu"
    student_email = "students.getstaff.student@test.edu"
    password = "StaffPass!234"

    _create_user(staff_email, password, roles=["staff"])
    student = _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(staff_email, password)

    response = client.get(
        f"/api/students/{student.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == student_email


def test_student_can_get_own_profile():
    """Test student can get their own profile"""
    student_email = "students.getself.student@test.edu"
    password = "StudentPass!234"

    student = _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(student_email, password)

    response = client.get(
        f"/api/students/{student.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == student_email


def test_student_cannot_get_other_profile():
    """Test student cannot get another student's profile"""
    student1_email = "students.getother.student1@test.edu"
    student2_email = "students.getother.student2@test.edu"
    password = "StudentPass!234"

    student1 = _create_user(student1_email, password, roles=["student"])
    _create_user(student2_email, password, roles=["student"])
    token = _get_auth_token(student2_email, password)

    response = client.get(
        f"/api/students/{student1.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_admin_can_update_student():
    """Test admin can update student"""
    admin_email = "students.update.admin@test.edu"
    student_email = "students.update.student@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    student = _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(admin_email, password)

    update_data = {
        "first_name": "Updated",
        "last_name": "Name"
    }

    response = client.put(
        f"/api/students/{student.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"


def test_staff_can_update_student():
    """Test staff can update student"""
    staff_email = "students.updatestaff.staff@test.edu"
    student_email = "students.updatestaff.student@test.edu"
    password = "StaffPass!234"

    _create_user(staff_email, password, roles=["staff"])
    student = _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(staff_email, password)

    update_data = {
        "first_name": "Updated",
        "last_name": "ByStaff"
    }

    response = client.put(
        f"/api/students/{student.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"


def test_student_cannot_update_student():
    """Test student cannot update students"""
    student1_email = "students.noupdate.student1@test.edu"
    student2_email = "students.noupdate.student2@test.edu"
    password = "StudentPass!234"

    student1 = _create_user(student1_email, password, roles=["student"])
    _create_user(student2_email, password, roles=["student"])
    student2_token = _get_auth_token(student2_email, password)

    update_data = {
        "first_name": "Hacked",
        "last_name": "Account"
    }

    response = client.put(
        f"/api/students/{student1.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {student2_token}"}
    )

    assert response.status_code == 403


def test_admin_can_delete_student():
    """Test admin can delete student"""
    admin_email = "students.delete.admin@test.edu"
    student_email = "students.delete.student@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    student = _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(admin_email, password)

    response = client.delete(
        f"/api/students/{student.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 204

    # Verify deleted
    get_response = client.get(
        f"/api/students/{student.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404


def test_staff_cannot_delete_student():
    """Test staff cannot delete students"""
    staff_email = "students.nodelete.staff@test.edu"
    student_email = "students.nodelete.student@test.edu"
    password = "StaffPass!234"

    _create_user(staff_email, password, roles=["staff"])
    student = _create_user(student_email, password, roles=["student"])
    staff_token = _get_auth_token(staff_email, password)

    response = client.delete(
        f"/api/students/{student.id}",
        headers={"Authorization": f"Bearer {staff_token}"}
    )

    assert response.status_code == 403


def test_student_cannot_delete_student():
    """Test student cannot delete students"""
    student1_email = "students.nodelete.student1@test.edu"
    student2_email = "students.nodelete.student2@test.edu"
    password = "StudentPass!234"

    student1 = _create_user(student1_email, password, roles=["student"])
    _create_user(student2_email, password, roles=["student"])
    student2_token = _get_auth_token(student2_email, password)

    response = client.delete(
        f"/api/students/{student1.id}",
        headers={"Authorization": f"Bearer {student2_token}"}
    )

    assert response.status_code == 403


def test_get_student_404():
    """Test 404 when student doesn't exist"""
    admin_email = "students.404@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    token = _get_auth_token(admin_email, password)

    fake_id = uuid4()
    response = client.get(
        f"/api/students/{fake_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404


def test_get_non_student_404():
    """Test 404 when trying to get non-student user"""
    admin_email = "students.nonstudent.admin@test.edu"
    other_admin_email = "students.nonstudent.other@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    other_admin = _create_user(other_admin_email, password, roles=["admin"])
    token = _get_auth_token(admin_email, password)

    # Try to get an admin user via students endpoint
    response = client.get(
        f"/api/students/{other_admin.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    assert "not a student" in response.json()["detail"].lower()
