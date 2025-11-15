"""Tests for Payment endpoints"""
from uuid import uuid4
from fastapi.testclient import TestClient

from app.db.models.compliance.finance import FinancialLedger
from app.db.session import SessionLocal
from app.main import app
from app.tests.utils import create_user_with_roles
from datetime import datetime, timezone

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


def _create_ledger_entry(user_id, line_type: str, amount_cents: int):
    """Helper to create a financial ledger entry"""
    session = SessionLocal()
    try:
        entry = FinancialLedger(
            user_id=user_id,
            line_type=line_type,
            amount_cents=amount_cents,
            description=f"Test {line_type}",
            created_at=datetime.now(timezone.utc)
        )
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return entry
    finally:
        session.close()


def _get_auth_token(email: str, password: str):
    """Helper to get JWT token"""
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_admin_can_list_all_transactions():
    """Test admin can list all financial transactions"""
    admin_email = "payments.list.admin@test.edu"
    student_email = "payments.list.student@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    student = _create_user(student_email, password, roles=["student"])

    # Create some ledger entries
    _create_ledger_entry(student.id, "tuition", 10000)
    _create_ledger_entry(student.id, "payment", 5000)

    token = _get_auth_token(admin_email, password)

    response = client.get(
        "/api/payments/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_finance_can_list_all_transactions():
    """Test finance role can list all financial transactions"""
    finance_email = "payments.listfin.finance@test.edu"
    student_email = "payments.listfin.student@test.edu"
    password = "FinancePass!234"

    _create_user(finance_email, password, roles=["finance"])
    student = _create_user(student_email, password, roles=["student"])

    _create_ledger_entry(student.id, "tuition", 10000)

    token = _get_auth_token(finance_email, password)

    response = client.get(
        "/api/payments/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_student_can_only_list_own_transactions():
    """Test student can only list their own transactions"""
    student_email = "payments.listself.student@test.edu"
    password = "StudentPass!234"

    student = _create_user(student_email, password, roles=["student"])
    _create_ledger_entry(student.id, "tuition", 10000)

    token = _get_auth_token(student_email, password)

    response = client.get(
        "/api/payments/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should only see their own
    assert all(entry["user_id"] == str(student.id) for entry in data)


def test_admin_can_record_payment():
    """Test admin can record a payment"""
    admin_email = "payments.record.admin@test.edu"
    student_email = "payments.record.student@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    student = _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(admin_email, password)

    payment_data = {
        "user_id": str(student.id),
        "amount_cents": 50000,
        "description": "Test payment"
    }

    response = client.post(
        "/api/payments/",
        json=payment_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == str(student.id)
    assert data["amount_cents"] == 50000
    assert data["line_type"] == "payment"


def test_finance_can_record_payment():
    """Test finance role can record a payment"""
    finance_email = "payments.recordfin.finance@test.edu"
    student_email = "payments.recordfin.student@test.edu"
    password = "FinancePass!234"

    _create_user(finance_email, password, roles=["finance"])
    student = _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(finance_email, password)

    payment_data = {
        "user_id": str(student.id),
        "amount_cents": 25000,
        "description": "Finance department payment"
    }

    response = client.post(
        "/api/payments/",
        json=payment_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201


def test_student_cannot_record_payment():
    """Test student cannot record payments"""
    student_email = "payments.norecord.student@test.edu"
    password = "StudentPass!234"

    student = _create_user(student_email, password, roles=["student"])
    token = _get_auth_token(student_email, password)

    payment_data = {
        "user_id": str(student.id),
        "amount_cents": 50000,
        "description": "Unauthorized payment"
    }

    response = client.post(
        "/api/payments/",
        json=payment_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_cannot_record_payment_for_nonexistent_user():
    """Test cannot record payment for user that doesn't exist"""
    admin_email = "payments.404@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    token = _get_auth_token(admin_email, password)

    fake_user_id = uuid4()
    payment_data = {
        "user_id": str(fake_user_id),
        "amount_cents": 50000
    }

    response = client.post(
        "/api/payments/",
        json=payment_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404


def test_admin_can_view_student_balance():
    """Test admin can view any student's balance"""
    admin_email = "payments.balance.admin@test.edu"
    student_email = "payments.balance.student@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    student = _create_user(student_email, password, roles=["student"])

    # Create charges and payments
    _create_ledger_entry(student.id, "tuition", 100000)  # $1000
    _create_ledger_entry(student.id, "fee", 5000)         # $50
    _create_ledger_entry(student.id, "payment", 60000)    # $600

    token = _get_auth_token(admin_email, password)

    response = client.get(
        f"/api/payments/balance/{student.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(student.id)
    assert data["total_charges_cents"] == 105000  # 1000 + 50
    assert data["total_payments_cents"] == 60000  # 600
    assert data["balance_cents"] == 45000         # 1050 - 600 = 450


def test_finance_can_view_student_balance():
    """Test finance role can view any student's balance"""
    finance_email = "payments.balancefin.finance@test.edu"
    student_email = "payments.balancefin.student@test.edu"
    password = "FinancePass!234"

    _create_user(finance_email, password, roles=["finance"])
    student = _create_user(student_email, password, roles=["student"])

    _create_ledger_entry(student.id, "tuition", 100000)

    token = _get_auth_token(finance_email, password)

    response = client.get(
        f"/api/payments/balance/{student.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_student_can_view_own_balance():
    """Test student can view their own balance"""
    student_email = "payments.balanceself.student@test.edu"
    password = "StudentPass!234"

    student = _create_user(student_email, password, roles=["student"])

    _create_ledger_entry(student.id, "tuition", 100000)
    _create_ledger_entry(student.id, "payment", 50000)

    token = _get_auth_token(student_email, password)

    response = client.get(
        f"/api/payments/balance/{student.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["balance_cents"] == 50000  # 1000 - 500


def test_student_cannot_view_other_balance():
    """Test student cannot view another student's balance"""
    student1_email = "payments.balanceother.student1@test.edu"
    student2_email = "payments.balanceother.student2@test.edu"
    password = "StudentPass!234"

    student1 = _create_user(student1_email, password, roles=["student"])
    _create_user(student2_email, password, roles=["student"])
    student2_token = _get_auth_token(student2_email, password)

    response = client.get(
        f"/api/payments/balance/{student1.id}",
        headers={"Authorization": f"Bearer {student2_token}"}
    )

    assert response.status_code == 403


def test_admin_can_view_payment_history():
    """Test admin can view any student's payment history"""
    admin_email = "payments.history.admin@test.edu"
    student_email = "payments.history.student@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    student = _create_user(student_email, password, roles=["student"])

    _create_ledger_entry(student.id, "tuition", 100000)
    _create_ledger_entry(student.id, "payment", 50000)

    token = _get_auth_token(admin_email, password)

    response = client.get(
        f"/api/payments/history/{student.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_finance_can_view_payment_history():
    """Test finance role can view any student's payment history"""
    finance_email = "payments.historyfin.finance@test.edu"
    student_email = "payments.historyfin.student@test.edu"
    password = "FinancePass!234"

    _create_user(finance_email, password, roles=["finance"])
    student = _create_user(student_email, password, roles=["student"])

    _create_ledger_entry(student.id, "tuition", 100000)

    token = _get_auth_token(finance_email, password)

    response = client.get(
        f"/api/payments/history/{student.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_student_can_view_own_history():
    """Test student can view their own payment history"""
    student_email = "payments.historyself.student@test.edu"
    password = "StudentPass!234"

    student = _create_user(student_email, password, roles=["student"])

    _create_ledger_entry(student.id, "tuition", 100000)
    _create_ledger_entry(student.id, "payment", 50000)

    token = _get_auth_token(student_email, password)

    response = client.get(
        f"/api/payments/history/{student.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(entry["user_id"] == str(student.id) for entry in data)


def test_student_cannot_view_other_history():
    """Test student cannot view another student's payment history"""
    student1_email = "payments.historyother.student1@test.edu"
    student2_email = "payments.historyother.student2@test.edu"
    password = "StudentPass!234"

    student1 = _create_user(student1_email, password, roles=["student"])
    _create_user(student2_email, password, roles=["student"])
    student2_token = _get_auth_token(student2_email, password)

    response = client.get(
        f"/api/payments/history/{student1.id}",
        headers={"Authorization": f"Bearer {student2_token}"}
    )

    assert response.status_code == 403


def test_balance_calculation_with_refunds():
    """Test balance calculation includes refunds"""
    admin_email = "payments.refund.admin@test.edu"
    student_email = "payments.refund.student@test.edu"
    password = "AdminPass!234"

    _create_user(admin_email, password, roles=["admin"])
    student = _create_user(student_email, password, roles=["student"])

    # Create charges and payments
    _create_ledger_entry(student.id, "tuition", 100000)   # $1000 charge
    _create_ledger_entry(student.id, "payment", 100000)   # $1000 payment
    _create_ledger_entry(student.id, "refund", 20000)     # $200 refund

    token = _get_auth_token(admin_email, password)

    response = client.get(
        f"/api/payments/balance/{student.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    # Charges: 1000, Payments + Refunds: 1000 + 200 = 1200
    # Balance: 1000 - 1200 = -200 (credit balance)
    assert data["balance_cents"] == -20000
