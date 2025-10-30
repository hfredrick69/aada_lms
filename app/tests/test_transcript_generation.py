from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db.session import SessionLocal
from app.main import app
from app.tests.utils import seed_student_program


def _reset_academic_tables() -> None:
    db = SessionLocal()
    try:
        db.execute(
            text(
                "TRUNCATE compliance.transcripts, compliance.credentials, compliance.refunds, compliance.withdrawals,"
                " compliance.financial_ledgers, module_progress, enrollments, modules, programs, users RESTART IDENTITY CASCADE"
            )
        )
        db.commit()
    finally:
        db.close()


def test_transcript_generation_flow():
    _reset_academic_tables()
    db = SessionLocal()
    seed = seed_student_program(db)

    client = TestClient(app)
    response = client.post(
        "/transcripts",
        json={
            "user_id": str(seed["student"].id),
            "program_id": str(seed["program"].id),
        },
    )
    assert response.status_code == 201, response.text
    transcript = response.json()
    assert transcript["user_id"] == str(seed["student"].id)
    assert len(transcript["modules"]) >= 1
    assert transcript["pdf_url"], "PDF URL should be present"

    pdf_path = Path(transcript["pdf_url"])
    assert pdf_path.exists(), "Transcript PDF should exist on disk"

    detail = client.get(f"/transcripts/{transcript['id']}")
    assert detail.status_code == 200
    assert detail.json()["modules"][0]["module_code"].startswith("MOD-")

    pdf_download = client.get(f"/transcripts/{transcript['id']}/pdf")
    assert pdf_download.status_code == 200
    assert pdf_download.headers["content-type"] == "application/pdf"

    db.close()
