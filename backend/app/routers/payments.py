"""Payment and invoice management router"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.compliance.finance import FinancialLedger
from app.routers.auth import get_current_user


class PaymentCreate(BaseModel):
    user_id: UUID
    program_id: Optional[UUID] = None
    amount_cents: int
    description: Optional[str] = None


class InvoiceLineItem(BaseModel):
    id: UUID
    user_id: UUID
    program_id: Optional[UUID]
    line_type: str
    amount_cents: int
    description: Optional[str]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StudentBalance(BaseModel):
    user_id: UUID
    total_charges_cents: int
    total_payments_cents: int
    balance_cents: int


router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/", response_model=List[InvoiceLineItem])
def list_all_transactions(
    user_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all financial transactions (admin can see all, students see only their own)"""
    query = db.query(FinancialLedger)

    # If specific user requested
    if user_id:
        query = query.filter(FinancialLedger.user_id == user_id)
    # Students can only see their own
    elif not any(role in ["admin", "finance"] for role in current_user.roles):
        query = query.filter(FinancialLedger.user_id == current_user.id)

    return query.order_by(FinancialLedger.created_at.desc()).all()


@router.get("/balance/{user_id}", response_model=StudentBalance)
def get_student_balance(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current balance for a student (charges - payments)"""
    # Check permissions (admin/finance can see any, students only their own)
    if user_id != current_user.id and not any(role in ["admin", "finance"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized to view this balance")

    # Calculate charges (tuition + fees)
    charges = db.query(func.sum(FinancialLedger.amount_cents)).filter(
        FinancialLedger.user_id == user_id,
        FinancialLedger.line_type.in_(["tuition", "fee"])
    ).scalar() or 0

    # Calculate payments + refunds
    payments = db.query(func.sum(FinancialLedger.amount_cents)).filter(
        FinancialLedger.user_id == user_id,
        FinancialLedger.line_type.in_(["payment", "refund"])
    ).scalar() or 0

    return StudentBalance(
        user_id=user_id,
        total_charges_cents=charges,
        total_payments_cents=payments,
        balance_cents=charges - payments
    )


@router.post("/", response_model=InvoiceLineItem, status_code=201)
def record_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record a payment (admin/finance only)"""
    # Only admin/finance can record payments
    if not any(role in ["admin", "finance"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized to record payments")

    # Verify user exists
    user = db.query(User).filter(User.id == payment.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create payment ledger entry
    ledger_entry = FinancialLedger(
        user_id=payment.user_id,
        program_id=payment.program_id,
        line_type="payment",
        amount_cents=payment.amount_cents,
        description=payment.description or "Payment received",
        created_at=datetime.utcnow()
    )

    db.add(ledger_entry)
    db.commit()
    db.refresh(ledger_entry)
    return ledger_entry


@router.get("/history/{user_id}", response_model=List[InvoiceLineItem])
def get_payment_history(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment history for a specific student"""
    # Check permissions
    if user_id != current_user.id and not any(role in ["admin", "finance"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized to view this history")

    return db.query(FinancialLedger).filter(
        FinancialLedger.user_id == user_id
    ).order_by(FinancialLedger.created_at.desc()).all()
