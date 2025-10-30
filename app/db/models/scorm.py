from sqlalchemy import Column, JSON, TIMESTAMP, Interval, String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class ScormRecord(Base):
    __tablename__ = "scorm_records"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"))
    lesson_status = Column(String)
    score_scaled = Column(Numeric(4,3))
    score_raw = Column(Numeric(6,2))
    session_time = Column(String)
    interactions = Column(JSON)
