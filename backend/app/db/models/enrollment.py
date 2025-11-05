from sqlalchemy import Column, String, Integer, ForeignKey, Date, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base


class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id", ondelete="CASCADE"))
    start_date = Column(Date, nullable=False)
    expected_end_date = Column(Date)
    status = Column(String, default="active")


class ModuleProgress(Base):
    __tablename__ = "module_progress"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    enrollment_id = Column(UUID(as_uuid=True), ForeignKey("enrollments.id", ondelete="CASCADE"))
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"))
    scorm_status = Column(String)  # incomplete/completed/passed/failed
    score = Column(Integer)
    progress_pct = Column(Integer)
    # Engagement tracking fields
    last_scroll_position = Column(Integer, default=0)  # Scroll offset in pixels
    active_time_seconds = Column(Integer, default=0)  # Time with page focused + activity
    sections_viewed = Column(JSON, default=list)  # List of section IDs viewed
    last_accessed_at = Column(TIMESTAMP(timezone=True))  # Last time progress was updated
