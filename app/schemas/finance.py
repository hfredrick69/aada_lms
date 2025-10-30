from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WithdrawalBase(BaseModel):
    enrollment_id: UUID
    requested_at: datetime
    reason: Optional[str] = None
    progress_pct_at_withdrawal: Optional[int] = Field(default=None, ge=0, le=100)


class WithdrawalCreate(WithdrawalBase):
    pass


class WithdrawalUpdate(BaseModel):
    reason: Optional[str] = None
    admin_processed_at: Optional[datetime] = None
    progress_pct_at_withdrawal: Optional[int] = Field(default=None, ge=0, le=100)


class WithdrawalRead(WithdrawalBase):
    id: UUID
    admin_processed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RefundBase(BaseModel):
    withdrawal_id: UUID
    policy_basis: Optional[str] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    remitted_at: Optional[datetime] = None


class RefundCreate(RefundBase):
    pass


class RefundUpdate(BaseModel):
    policy_basis: Optional[str] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    remitted_at: Optional[datetime] = None
    amount_cents: Optional[int] = Field(default=None, ge=0)


class RefundRead(RefundBase):
    id: UUID
    amount_cents: int

    model_config = ConfigDict(from_attributes=True)
