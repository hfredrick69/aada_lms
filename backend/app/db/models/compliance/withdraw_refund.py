from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base


class Withdrawal(Base):
    __tablename__ = "withdrawals"
    __table_args__ = {"schema": "compliance"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    enrollment_id = Column(UUID(as_uuid=True), ForeignKey("enrollments.id", ondelete="CASCADE"))
    requested_at = Column(TIMESTAMP(timezone=True), nullable=False)
    reason = Column(Text)
    admin_processed_at = Column(TIMESTAMP(timezone=True))
    progress_pct_at_withdrawal = Column(Integer)  # for ≤50% calculation


class Refund(Base):
    __tablename__ = "refunds"
    __table_args__ = {"schema": "compliance"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    withdrawal_id = Column(UUID(as_uuid=True), ForeignKey("compliance.withdrawals.id", ondelete="CASCADE"))
    amount_cents = Column(Integer, nullable=False)
    policy_basis = Column(Text)     # notes for GNPEC Std 12 calculation
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(TIMESTAMP(timezone=True))
    remitted_at = Column(TIMESTAMP(timezone=True))  # enforce <=45 days
