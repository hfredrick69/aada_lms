"""Tests for User endpoints"""
from uuid import uuid4
from fastapi.testclient import TestClient

from app.core.security import get_password_hash
from app.db.models.role import Role
from app.db.models.user import User
from app.db.session import SessionLocal
from app.main import app

client = TestClient(app)


def _create_user(email: str, password: str, roles: list[str] | None = None):
    """Helper to create user with roles"""
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.email == email).first()
        if user:
            session.delete(user)
            session.commit()

        user = User(
            email=email,
            password_hash=get_password_hash(password),
            first_name="Unit",
            last_name="Test",
            status="active",
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        for role_name in roles or []:
            role = session.query(Role).filter(Role.name == role_name).first()
            if not role:
                role = Role(name=role_name, description=f"{role_name} role")
                session.add(role)
                session.commit()
                session.refresh(role)
            user.roles.append(role)
        session.commit()
        session.refresh(user)
        session.expunge_all()
        return user
    finally:
        session.close()


def _get_auth_token(email: str, password: str):
    """Helper to get JWT token"""
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_admin_can_list_users():
    """Test admin can list all users"""
    admin_email = "users.list.admin@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    token = _get_auth_token(admin_email, password)

    response = client.get(
        "/api/users/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_student_cannot_list_users():
    """Test student cannot list users"""
    student_email = "users.nolist.student@test.edu"
    password = "StudentPass!234"

    _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(student_email, password)

    response = client.get(
        "/api/users/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_admin_can_create_user():
    """Test admin can create new user"""
    admin_email = "users.create.admin@test.edu"
    new_user_email = f"user.{uuid4()}@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    token = _get_auth_token(admin_email, password)

    user_data = {
        "email": new_user_email,
        "password": "NewUserPass!234",
        "first_name": "New",
        "last_name": "User"
    }

    response = client.post(
        "/api/users/",
        json=user_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == new_user_email
    assert data["first_name"] == "New"
    assert data["last_name"] == "User"


def test_student_cannot_create_user():
    """Test student cannot create users"""
    student_email = "users.nocreate.student@test.edu"
    new_user_email = f"user.{uuid4()}@test.edu"
    password = "StudentPass!234"

    _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(student_email, password)

    user_data = {
        "email": new_user_email,
        "password": "NewUserPass!234",
        "first_name": "New",
        "last_name": "User"
    }

    response = client.post(
        "/api/users/",
        json=user_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_cannot_create_duplicate_email():
    """Test cannot create user with duplicate email"""
    admin_email = "users.dup.admin@test.edu"
    duplicate_email = "users.duplicate@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    _create_user(duplicate_email, password, roles=["student"])
    token = _get_auth_token(admin_email, password)

    user_data = {
        "email": duplicate_email,
        "password": "NewUserPass!234",
        "first_name": "Duplicate",
        "last_name": "User"
    }

    response = client.post(
        "/api/users/",
        json=user_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_admin_can_get_user():
    """Test admin can get any user by ID"""
    admin_email = "users.get.admin@test.edu"
    student_email = "users.get.student@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    student = _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(admin_email, password)

    response = client.get(
        f"/api/users/{student.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == student_email


def test_user_can_get_own_profile():
    """Test user can get their own profile"""
    student_email = "users.getself.student@test.edu"
    password = "StudentPass!234"

    student = _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(student_email, password)

    response = client.get(
        f"/api/users/{student.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == student_email


def test_user_cannot_get_other_profile():
    """Test user cannot get another user's profile"""
    student1_email = "users.getother.student1@test.edu"
    student2_email = "users.getother.student2@test.edu"
    password = "StudentPass!234"

    student1 = _create_user(student1_email, password, roles=["student"])
    _create_user(student2_email, password, roles=["student"])
    token = _get_auth_token(student2_email, password)

    response = client.get(
        f"/api/users/{student1.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_admin_can_update_user():
    """Test admin can update user"""
    admin_email = "users.update.admin@test.edu"
    student_email = "users.update.student@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    student = _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(admin_email, password)

    update_data = {
        "first_name": "Updated",
        "last_name": "Name"
    }

    response = client.put(
        f"/api/users/{student.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"


def test_student_cannot_update_user():
    """Test student cannot update users"""
    admin_email = "users.noupdate.admin@test.edu"
    student_email = "users.noupdate.student@test.edu"
    password = "AdminPass!234"

    admin = _create_user(admin_email, password, roles=["admin"])
    _create_user(student_email, password, roles=["student"])
    student_token = _get_auth_token(student_email, password)

    update_data = {
        "first_name": "Hacked",
        "last_name": "Account"
    }

    response = client.put(
        f"/api/users/{admin.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == 403


def test_admin_can_delete_user():
    """Test admin can delete user"""
    admin_email = "users.delete.admin@test.edu"
    student_email = "users.delete.student@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    student = _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(admin_email, password)

    response = client.delete(
        f"/api/users/{student.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 204

    # Verify deleted
    get_response = client.get(
        f"/api/users/{student.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404


def test_student_cannot_delete_user():
    """Test student cannot delete users"""
    admin_email = "users.nodelete.admin@test.edu"
    student_email = "users.nodelete.student@test.edu"
    password = "AdminPass!234"

    admin = _create_user(admin_email, password, roles=["admin"])
    _create_user(student_email, password, roles=["student"])
    student_token = _get_auth_token(student_email, password)

    response = client.delete(
        f"/api/users/{admin.id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == 403


def test_get_user_404():
    """Test 404 when user doesn't exist"""
    admin_email = "users.404@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    token = _get_auth_token(admin_email, password)

    fake_id = uuid4()
    response = client.get(
        f"/api/users/{fake_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
