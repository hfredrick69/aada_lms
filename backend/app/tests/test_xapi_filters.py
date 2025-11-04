from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db.session import SessionLocal
from app.main import app


def _clear_xapi() -> None:
    db = SessionLocal()
    try:
        db.execute(text("TRUNCATE xapi_statements RESTART IDENTITY CASCADE"))
        db.commit()
    finally:
        db.close()


def test_xapi_filters_by_agent_and_since():
    _clear_xapi()
    client = TestClient(app)
    base_payload = {
        "actor": {"name": "Student One", "mbox": "mailto:student1@example.com"},
        "object": {"id": "activity-1", "definition": {"name": "Module 1"}},
        "result": {"score": {"raw": 95}},
        "context": {"platform": "lms"},
    }
    first_timestamp = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    second_timestamp = datetime(2024, 5, 1, 12, 0, tzinfo=timezone.utc)

    verbs = [
        {"id": "http://adlnet.gov/expapi/verbs/launched", "display": {"en-US": "launched"}},
        {"id": "http://adlnet.gov/expapi/verbs/completed", "display": {"en-US": "completed"}},
    ]

    client.post(
        "/xapi/statements",
        json={**base_payload, "verb": verbs[0], "timestamp": first_timestamp.isoformat()},
    )
    client.post(
        "/xapi/statements",
        json={
            **base_payload,
            "verb": verbs[1],
            "timestamp": second_timestamp.isoformat(),
            "actor": {"name": "Student Two", "mbox": "mailto:student2@example.com"},
        },
    )

    filtered = client.get(
        "/xapi/statements",
        params={"agent": "student1@example.com", "since": "2023-12-31T00:00:00Z"},
    )
    assert filtered.status_code == 200
    statements = filtered.json()
    assert len(statements) == 1
    assert statements[0]["verb"]["id"] == verbs[0]["id"]

    verb_filter = client.get(
        "/xapi/statements",
        params={"verb": "completed"},
    )
    assert verb_filter.status_code == 200
    verb_statements = verb_filter.json()
    assert len(verb_statements) == 1
    assert verb_statements[0]["verb"]["id"] == verbs[1]["id"]
