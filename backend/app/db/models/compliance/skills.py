from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base


class SkillCheckoff(Base):
    __tablename__ = "skills_checkoffs"
    __table_args__ = {"schema": "compliance"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"))
    skill_code = Column(String, nullable=False)    # e.g., PPE_DON_DOFF
    status = Column(String, nullable=False, default="pending")  # pending/approved/rejected
    evaluator_name = Column(String)
    evaluator_license = Column(String)
    evidence_url = Column(Text)
    signed_at = Column(TIMESTAMP(timezone=True))
