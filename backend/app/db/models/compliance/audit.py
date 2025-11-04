from sqlalchemy import Column, String, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = {"schema": "compliance"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    action = Column(String, nullable=False)
    entity = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    details = Column(Text)
    occurred_at = Column(TIMESTAMP(timezone=True))
