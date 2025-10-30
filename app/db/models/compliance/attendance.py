from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"
    __table_args__ = {"schema": "compliance"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"))
    session_type = Column(String, nullable=False)  # live, lab, externship
    session_ref = Column(String)                   # Zoom ID or lab code
    started_at = Column(TIMESTAMP(timezone=True), nullable=False)
    ended_at = Column(TIMESTAMP(timezone=True), nullable=False)
