from datetime import datetime, timedelta, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.compliance.finance import FinancialLedger
from app.db.models.compliance.withdraw_refund import Refund, Withdrawal
from app.db.models.enrollment import Enrollment
from app.db.session import get_db
from app.schemas.finance import (
    RefundCreate,
    RefundRead,
    RefundUpdate,
    WithdrawalCreate,
    WithdrawalRead,
    WithdrawalUpdate,
)

router = APIRouter(prefix="/finance", tags=["finance"])


def _get_withdrawal(db: Session, withdrawal_id: UUID) -> Withdrawal:
    record = db.get(Withdrawal, withdrawal_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Withdrawal not found")
    return record


def _get_refund(db: Session, refund_id: UUID) -> Refund:
    record = db.get(Refund, refund_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refund not found")
    return record


def _load_enrollment(db: Session, enrollment_id: UUID) -> Enrollment:
    enrollment = db.get(Enrollment, enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    return enrollment


def _is_cancellation(withdrawal: Withdrawal, enrollment: Enrollment) -> bool:
    if not enrollment.start_date:
        return False
    start_dt = datetime.combine(enrollment.start_date, datetime.min.time(), tzinfo=timezone.utc)
    requested_at = withdrawal.requested_at
    if requested_at.tzinfo is None:
        requested_at = requested_at.replace(tzinfo=timezone.utc)
    return requested_at <= start_dt + timedelta(hours=settings.CANCELLATION_WINDOW_HOURS)


def _sum_tuition(db: Session, enrollment: Enrollment) -> int:
    total = (
        db.query(func.coalesce(func.sum(FinancialLedger.amount_cents), 0))
        .filter(
            FinancialLedger.user_id == enrollment.user_id,
            FinancialLedger.program_id == enrollment.program_id,
            FinancialLedger.line_type.in_(["tuition", "fee"]),
        )
        .scalar()
    )
    if total is None or total <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tuition or fee records found to calculate refund.",
        )
    return int(total)


def _calculate_refund(db: Session, withdrawal: Withdrawal) -> tuple[int, str]:
    enrollment = _load_enrollment(db, withdrawal.enrollment_id)
    total_tuition = _sum_tuition(db, enrollment)
    progress_pct = withdrawal.progress_pct_at_withdrawal or 0
    if _is_cancellation(withdrawal, enrollment):
        return total_tuition, "Full refund within 72-hour cancellation window."
    if progress_pct < settings.PROGRESS_REFUND_THRESHOLD:
        prorated = int(round(total_tuition * (1 - (progress_pct / 100))))
        return prorated, f"Prorated refund based on {progress_pct}% completion."
    return 0, f"No refund – completion at {progress_pct}% exceeds policy threshold."


def _validate_remittance(approved_at: datetime | None, remitted_at: datetime | None) -> None:
    if approved_at and remitted_at:
        if approved_at.tzinfo is None:
            approved_at = approved_at.replace(tzinfo=timezone.utc)
        if remitted_at.tzinfo is None:
            remitted_at = remitted_at.replace(tzinfo=timezone.utc)
        if remitted_at > approved_at + timedelta(days=settings.REFUND_DAYS_LIMIT):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refund remittance must occur within 45 days of approval.",
            )


@router.get("/withdrawals", response_model=List[WithdrawalRead])
def list_withdrawals(db: Session = Depends(get_db)) -> List[WithdrawalRead]:
    return db.query(Withdrawal).order_by(Withdrawal.requested_at.desc()).all()


@router.post("/withdrawals", response_model=WithdrawalRead, status_code=status.HTTP_201_CREATED)
def create_withdrawal(
    payload: WithdrawalCreate, db: Session = Depends(get_db)
) -> WithdrawalRead:
    _load_enrollment(db, payload.enrollment_id)
    record = Withdrawal(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/withdrawals/{withdrawal_id}", response_model=WithdrawalRead)
def get_withdrawal(withdrawal_id: UUID, db: Session = Depends(get_db)) -> WithdrawalRead:
    return _get_withdrawal(db, withdrawal_id)


@router.put("/withdrawals/{withdrawal_id}", response_model=WithdrawalRead)
def update_withdrawal(
    withdrawal_id: UUID, payload: WithdrawalUpdate, db: Session = Depends(get_db)
) -> WithdrawalRead:
    record = _get_withdrawal(db, withdrawal_id)
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)
    if update_data:
        record.admin_processed_at = update_data.get("admin_processed_at", datetime.now(timezone.utc))
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/withdrawals/{withdrawal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_withdrawal(withdrawal_id: UUID, db: Session = Depends(get_db)) -> None:
    record = _get_withdrawal(db, withdrawal_id)
    db.delete(record)
    db.commit()


@router.get("/refunds", response_model=List[RefundRead])
def list_refunds(db: Session = Depends(get_db)) -> List[RefundRead]:
    return db.query(Refund).order_by(Refund.approved_at.desc().nullslast(), Refund.id).all()


@router.post("/refunds", response_model=RefundRead, status_code=status.HTTP_201_CREATED)
def create_refund(payload: RefundCreate, db: Session = Depends(get_db)) -> RefundRead:
    withdrawal = _get_withdrawal(db, payload.withdrawal_id)
    amount_cents, basis = _calculate_refund(db, withdrawal)
    data = payload.model_dump()
    approved_at = data.get("approved_at") or datetime.now(timezone.utc)
    remitted_at = data.get("remitted_at")
    _validate_remittance(approved_at, remitted_at)
    record = Refund(
        withdrawal_id=withdrawal.id,
        amount_cents=amount_cents,
        policy_basis=data.get("policy_basis") or basis,
        approved_by=data.get("approved_by"),
        approved_at=approved_at,
        remitted_at=remitted_at,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/refunds/{refund_id}", response_model=RefundRead)
def get_refund(refund_id: UUID, db: Session = Depends(get_db)) -> RefundRead:
    return _get_refund(db, refund_id)


@router.put("/refunds/{refund_id}", response_model=RefundRead)
def update_refund(
    refund_id: UUID, payload: RefundUpdate, db: Session = Depends(get_db)
) -> RefundRead:
    record = _get_refund(db, refund_id)
    update_data = payload.model_dump(exclude_unset=True)
    if "approved_at" in update_data:
        record.approved_at = update_data["approved_at"]
    if "remitted_at" in update_data:
        _validate_remittance(update_data.get("approved_at") or record.approved_at, update_data["remitted_at"])
        record.remitted_at = update_data["remitted_at"]
    if "approved_by" in update_data:
        record.approved_by = update_data["approved_by"]
    if "policy_basis" in update_data:
        record.policy_basis = update_data["policy_basis"]
    if "amount_cents" in update_data:
        record.amount_cents = update_data["amount_cents"]
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/refunds/{refund_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_refund(refund_id: UUID, db: Session = Depends(get_db)) -> None:
    record = _get_refund(db, refund_id)
    db.delete(record)
    db.commit()
