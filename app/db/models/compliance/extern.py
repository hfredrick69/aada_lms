from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class Externship(Base):
    __tablename__ = "externships"
    __table_args__ = {"schema": "compliance"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    site_name = Column(String, nullable=False)
    site_address = Column(Text)
    supervisor_name = Column(String)
    supervisor_email = Column(String)
    total_hours = Column(Integer, default=0)
    verified = Column(Boolean, default=False)
    verification_doc_url = Column(Text)
    verified_at = Column(TIMESTAMP(timezone=True))
