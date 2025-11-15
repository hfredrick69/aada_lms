from __future__ import annotations

import os
from typing import Any, Dict, Optional
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine import make_url

# Ensure tests use a reachable database (defaults to local Postgres via docker)
DEFAULT_TEST_DB = (
    "postgresql+psycopg2://aada:HLARcCjjFCBZQB8IIevlz1EEt8zaR9M9@localhost:5432/aada_lms_test"
)
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", DEFAULT_TEST_DB)
os.environ.setdefault("DATABASE_URL", TEST_DATABASE_URL)

from app.db import session as session_module  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.models.role import Role  # noqa: E402
from app.db.models.user import User  # noqa: E402
from app.db.models.program import Program, Module  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from app.utils.encryption import encrypt_value  # noqa: E402
# Ensure the dedicated test database exists
test_db_url = make_url(TEST_DATABASE_URL)
admin_url = test_db_url.set(database="postgres")
with create_engine(admin_url, isolation_level="AUTOCOMMIT").connect() as conn:
    exists = conn.execute(
        text("SELECT 1 FROM pg_database WHERE datname = :name"),
        {"name": test_db_url.database},
    ).scalar()
    if not exists:
        conn.execute(text(f'CREATE DATABASE "{test_db_url.database}"'))

from app.main import app  # noqa: E402

# Rebind the session/engine to the dedicated test database
engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session_module.engine = engine
session_module.SessionLocal = TestingSessionLocal

with engine.begin() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS crm"))
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS compliance"))
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


class ApiClient:
    """Wrap FastAPI TestClient to allow shorthand paths without /api prefix."""

    def __init__(self, raw_client: TestClient):
        self._client = raw_client

    @staticmethod
    def _normalize_path(path: str) -> str:
        if not path:
            return "/"
        normalized = path if path.startswith("/") else f"/{path}"
        if normalized == "/" or normalized.startswith("/api") or normalized.startswith("/docs"):
            return normalized
        if normalized.startswith("/openapi") or normalized.startswith("/static"):
            return normalized
        return f"/api{normalized}"

    def get(self, path: str, *args, **kwargs):
        return self._client.get(self._normalize_path(path), *args, **kwargs)

    def post(self, path: str, *args, **kwargs):
        return self._client.post(self._normalize_path(path), *args, **kwargs)

    def put(self, path: str, *args, **kwargs):
        return self._client.put(self._normalize_path(path), *args, **kwargs)

    def patch(self, path: str, *args, **kwargs):
        return self._client.patch(self._normalize_path(path), *args, **kwargs)

    def delete(self, path: str, *args, **kwargs):
        return self._client.delete(self._normalize_path(path), *args, **kwargs)

    def __getattr__(self, item: str):
        return getattr(self._client, item)


def _ensure_role(db: Session, role_name: str, description: Optional[str] = None) -> Role:
    role = db.query(Role).filter(Role.name == role_name).first()
    if role:
        return role
    role = Role(name=role_name, description=description or f"{role_name.title()} role")
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def _create_user(
    db: Session,
    *,
    email: Optional[str] = None,
    password: str = "TestPass!23",
    roles: Optional[list[str]] = None,
) -> Dict[str, Any]:
    email = email or f"user_{uuid4().hex[:8]}@example.edu"
    encrypted_email = encrypt_value(db, email)
    encrypted_first = encrypt_value(db, "Test")
    encrypted_last = encrypt_value(db, "User")

    existing = db.query(User).filter(User.email == encrypted_email).first()
    if existing:
        db.delete(existing)
        db.commit()

    user = User(
        email=encrypted_email,
        password_hash=get_password_hash(password),
        first_name=encrypted_first,
        last_name=encrypted_last,
        status="active",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    for role_name in roles or []:
        role = _ensure_role(db, role_name)
        if role not in user.roles:
            user.roles.append(role)

    db.add(user)
    db.commit()
    db.refresh(user)
    db.expunge(user)
    # Attach plain-text helpers for test readability (detached instance)
    setattr(user, "email_plain", email)
    setattr(user, "email", email)
    setattr(user, "first_name", "Test")
    setattr(user, "last_name", "User")
    return {"user": user, "password": password, "email": email}


@pytest.fixture()
def db() -> Session:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client() -> ApiClient:
    return ApiClient(TestClient(app))


@pytest.fixture()
def admin_user(db: Session) -> Dict[str, Any]:
    return _create_user(
        db,
        email=f"admin_{uuid4().hex[:6]}@example.edu",
        password="AdminPass!23",
        roles=["admin"],
    )


@pytest.fixture()
def admin_token(client: ApiClient, admin_user: Dict[str, Any]) -> str:
    payload = {"email": admin_user["email"], "password": admin_user["password"]}
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture()
def auth_headers(admin_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture()
def test_user(db: Session) -> User:
    results = _create_user(
        db,
        email=f"student_{uuid4().hex[:6]}@example.edu",
        password="StudentPass!23",
        roles=["student"],
    )
    return results["user"]


@pytest.fixture()
def test_program(db: Session) -> Program:
    program = Program(
        code=f"PRG-{uuid4().hex[:6]}",
        name="Pytest Program",
        credential_level="certificate",
        total_clock_hours=120,
    )
    db.add(program)
    db.commit()
    db.refresh(program)
    return program


@pytest.fixture()
def test_module(db: Session, test_program: Program) -> Module:
    module = Module(
        program_id=test_program.id,
        code=f"MOD-{uuid4().hex[:4]}",
        title="Pytest Module",
        delivery_type="online",
        clock_hours=12,
        requires_in_person=False,
        position=1,
    )
    db.add(module)
    db.commit()
    db.refresh(module)
    return module
