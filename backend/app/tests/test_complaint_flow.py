from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db.session import SessionLocal
from app.main import app


def _clear_complaints_table() -> None:
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM compliance.complaints"))
        db.commit()
    finally:
        db.close()


def test_complaint_lifecycle():
    _clear_complaints_table()
    client = TestClient(app)
    response = client.get("/complaints")
    assert response.status_code == 200
    assert response.json() == []

    payload = {
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "category": "instruction",
        "details": "Instructor missed scheduled labs.",
    }
    create_resp = client.post("/complaints", json=payload)
    assert create_resp.status_code == 201, create_resp.text
    complaint = create_resp.json()
    assert complaint["status"] == "open"
    assert "gnpec@tcsg.edu" in complaint["gnpec_appeal_info"]

    complaint_id = complaint["id"]
    review_resp = client.put(f"/complaints/{complaint_id}", json={"status": "in_review"})
    assert review_resp.status_code == 200
    assert review_resp.json()["status"] == "in_review"

    resolve_resp = client.put(
        f"/complaints/{complaint_id}",
        json={
            "status": "resolved",
            "resolution_notes": "Provided make-up labs.",
        },
    )
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["status"] == "resolved"

    appeal_resp = client.put(
        f"/complaints/{complaint_id}",
        json={"status": "appealed"},
    )
    assert appeal_resp.status_code == 200
    assert appeal_resp.json()["status"] == "appealed"
