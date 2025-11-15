from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.tests.utils import create_user_with_roles

client = TestClient(app)


def _create_user(email: str, password: str, roles: list[str] | None = None) -> None:
    session = SessionLocal()
    try:
        create_user_with_roles(session, email=email, password=password, roles=roles)
    finally:
        session.close()


def test_login_and_me_flow():
    email = "auth.test@aada.edu"
    password = "TestPasswd!23"
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
