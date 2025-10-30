from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class Program(Base):
    __tablename__ = "programs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    credential_level = Column(String, nullable=False)  # 'certificate'
    total_clock_hours = Column(Integer, nullable=False)

class Module(Base):
    __tablename__ = "modules"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id", ondelete="CASCADE"))
    code = Column(String, nullable=False)
    title = Column(String, nullable=False)
    delivery_type = Column(String, nullable=False)     # 'online','hybrid','in_person'
    clock_hours = Column(Integer, nullable=False)
    requires_in_person = Column(Boolean, default=False)
    position = Column(Integer, nullable=False)
