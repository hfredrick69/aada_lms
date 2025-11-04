from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base


class Complaint(Base):
    __tablename__ = "complaints"
    __table_args__ = {"schema": "compliance"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    submitted_at = Column(TIMESTAMP(timezone=True), nullable=False)
    category = Column(String)
    details = Column(Text, nullable=False)
    status = Column(String, default="open")  # open/in_review/resolved/appealed
    resolution_notes = Column(Text)
    resolution_at = Column(TIMESTAMP(timezone=True))
