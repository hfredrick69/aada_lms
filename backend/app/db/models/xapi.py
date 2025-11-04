from sqlalchemy import Column, JSON, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base


class XapiStatement(Base):
    __tablename__ = "xapi_statements"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor = Column(JSON, nullable=False)
    verb = Column(JSON, nullable=False)
    object = Column(JSON, nullable=False)
    result = Column(JSON)
    context = Column(JSON)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    stored_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
