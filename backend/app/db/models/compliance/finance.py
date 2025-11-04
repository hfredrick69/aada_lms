from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base


class FinancialLedger(Base):
    __tablename__ = "financial_ledgers"
    __table_args__ = {"schema": "compliance"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id", ondelete="SET NULL"))
    line_type = Column(String, nullable=False)  # tuition, fee, payment, refund
    amount_cents = Column(Integer, nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True))
