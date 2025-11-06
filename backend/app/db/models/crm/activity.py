"""Activity model for CRM - tracks all interactions with leads/applications."""

from sqlalchemy import Column, String, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base


class Activity(Base):
    """Activity - communication log for leads, applications, users."""
    __tablename__ = "activities"
    __table_args__ = {"schema": "crm"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Polymorphic entity tracking (lead, application, user)
    entity_type = Column(String(50), nullable=False)  # lead, application, user
    entity_id = Column(UUID(as_uuid=True), nullable=False)

    # Activity details
    activity_type = Column(String(50), nullable=False)  # call, email, sms, meeting, note, task
    subject = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    # Task scheduling
    due_date = Column(TIMESTAMP(timezone=True), nullable=True)
    completed_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Assignment
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
