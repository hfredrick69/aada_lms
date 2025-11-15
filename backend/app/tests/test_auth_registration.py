import uuid
from unittest.mock import patch
from urllib.parse import urlparse, parse_qs

from fastapi.testclient import TestClient

from app.core.security import get_password_hash
from app.db.models.role import Role
from app.db.models.user import User
from app.db.session import SessionLocal
from app.main import app
from app.utils.encryption import encrypt_value


client = TestClient(app)


def _create_student(email: str, password: str) -> None:
    session = SessionLocal()
    try:
        student_role = session.query(Role).filter(Role.name == "student").first()
        if not student_role:
            student_role = Role(name="student", description="Student")
            session.add(student_role)
            session.flush()

        user = User(
            email=encrypt_value(session, email),
            password_hash=get_password_hash(password),
            first_name=encrypt_value(session, "Test"),
            last_name=encrypt_value(session, "User"),
            status="active",
        )
        user.roles.append(student_role)
        session.add(user)
        session.commit()
    finally:
        session.close()


def _extract_token_from_link(link: str) -> str:
    parsed = urlparse(link)
    token = parse_qs(parsed.query).get("token")
    return token[0] if token else ""


def test_registration_flow_creates_student_user():
    email = f"{uuid.uuid4().hex}@example.edu"

    with patch("app.routers.auth.send_registration_verification_email") as mock_email:
        response = client.post("/api/auth/register/request", json={"email": email})
        assert response.status_code == 202
        assert mock_email.called
        link = mock_email.call_args.args[1]
        verification_token = _extract_token_from_link(link)

    verify_response = client.post("/api/auth/register/verify", json={"token": verification_token})
    assert verify_response.status_code == 200
    registration_token = verify_response.json()["registration_token"]

    complete_payload = {
        "registration_token": registration_token,
        "first_name": "Test",
        "last_name": "Student",
        "password": "ValidPass123!",
    }
    complete_response = client.post("/api/auth/register/complete", json=complete_payload)
    assert complete_response.status_code == 201

    login_response = client.post("/api/auth/login", json={"email": email, "password": complete_payload["password"]})
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_registration_request_is_silent_for_existing_user():
    email = f"existing-{uuid.uuid4().hex}@example.edu"
    _create_student(email, "AnotherPass123!")

    with patch("app.routers.auth.send_registration_verification_email") as mock_email:
        response = client.post("/api/auth/register/request", json={"email": email})
        assert response.status_code == 202
        mock_email.assert_not_called()
