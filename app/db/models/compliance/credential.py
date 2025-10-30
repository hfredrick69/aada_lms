from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class Credential(Base):
    __tablename__ = "credentials"
    __table_args__ = {"schema": "compliance"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id", ondelete="CASCADE"))
    credential_type = Column(String, nullable=False)  # 'certificate'
    issued_at = Column(TIMESTAMP(timezone=True), nullable=False)
    cert_serial = Column(String, unique=True, nullable=False)
