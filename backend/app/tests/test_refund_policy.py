from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db.models.compliance.withdraw_refund import Withdrawal
from app.db.session import SessionLocal
from app.main import app
from app.tests.utils import seed_student_program


def _reset_finance_tables() -> None:
    db = SessionLocal()
    try:
        db.execute(
            text(
                "TRUNCATE compliance.refunds, compliance.withdrawals, compliance.financial_ledgers,"
                " module_progress, enrollments, modules, programs, users RESTART IDENTITY CASCADE"
            )
        )
        db.commit()
    finally:
        db.close()


def test_refunds_list():
    _reset_finance_tables()
    client = TestClient(app)
    r = client.get("/api/finance/refunds")
    assert r.status_code == 200
    assert r.json() == []


def test_prorated_refund_calculation():
    _reset_finance_tables()
    db = SessionLocal()
    seed = seed_student_program(
        db,
        module_progress=(
            {"progress_pct": 40, "score": 82, "scorm_status": "incomplete"},
            {"progress_pct": 40, "score": 84, "scorm_status": "incomplete"},
        ),
    )
    withdrawal = Withdrawal(
        id=uuid4(),
        enrollment_id=seed["enrollment"].id,
        requested_at=seed["now"],
        reason="Student withdrew mid program",
        progress_pct_at_withdrawal=40,
    )
    db.add(withdrawal)
    db.commit()

    client = TestClient(app)
    response = client.post(
        "/api/finance/refunds",
        json={
            "withdrawal_id": str(withdrawal.id),
            "approved_by": str(seed["admin"].id),
        },
    )
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["amount_cents"] == 60000  # 60% refund of 100000 tuition
    assert "Prorated refund" in payload["policy_basis"]
    db.close()


def test_cancellation_full_refund():
    _reset_finance_tables()
    db = SessionLocal()
    seed = seed_student_program(db)
    requested_at = datetime.combine(seed["enrollment"].start_date, datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=12)  # noqa: E501
    withdrawal = Withdrawal(
        id=uuid4(),
        enrollment_id=seed["enrollment"].id,
        requested_at=requested_at,
        reason="Cancelled within window",
        progress_pct_at_withdrawal=5,
    )
    db.add(withdrawal)
    db.commit()

    client = TestClient(app)
    response = client.post(
        "/api/finance/refunds",
        json={
            "withdrawal_id": str(withdrawal.id),
            "approved_by": str(seed["admin"].id),
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["amount_cents"] == 100000
    assert "Full refund" in payload["policy_basis"]

    db.close()
