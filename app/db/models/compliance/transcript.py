from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class Transcript(Base):
    __tablename__ = "transcripts"
    __table_args__ = {"schema": "compliance"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id", ondelete="CASCADE"))
    gpa = Column(Numeric(3,2))
    generated_at = Column(TIMESTAMP(timezone=True))
    pdf_url = Column(Text)
