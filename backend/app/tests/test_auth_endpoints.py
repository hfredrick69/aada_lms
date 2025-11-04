from fastapi.testclient import TestClient

from app.core.security import get_password_hash
from app.db.models.role import Role
from app.db.models.user import User
from app.db.session import SessionLocal
from app.main import app

client = TestClient(app)


def _create_user(email: str, password: str, roles: list[str] | None = None) -> None:
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
                role = Role(name=role_name)
                session.add(role)
                session.commit()
                session.refresh(role)
            user.roles.append(role)
        session.add(user)
        session.commit()
    finally:
        session.close()


def test_login_and_me_flow():
    email = "auth.test@aada.edu"
    password = "TestPass!23"
    _create_user(email, password, roles=["Admin", "Finance"])

    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    token = data["access_token"]

    me_response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    profile = me_response.json()
    assert profile["email"].lower() == email.lower()
    assert set(profile["roles"]) == {"Admin", "Finance"}


def test_login_invalid_credentials_returns_401():
    email = "invalid@aada.edu"
    password = "InvalidPass!23"
    _create_user(email, password, roles=["Registrar"])

    response = client.post("/api/auth/login", json={"email": email, "password": "wrongpass"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

    response_missing = client.post("/api/auth/login", json={"email": "notfound@aada.edu", "password": "anypass"})
    assert response_missing.status_code == 401
