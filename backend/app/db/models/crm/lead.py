"""Lead and LeadSource models for CRM."""

from sqlalchemy import Column, String, Integer, Text, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base


class LeadSource(Base):
    """Lead source - where the lead came from."""
    __tablename__ = "lead_sources"
    __table_args__ = {"schema": "crm"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    leads = relationship("Lead", back_populates="lead_source")


class Lead(Base):
    """Lead - potential student who has shown interest."""
    __tablename__ = "leads"
    __table_args__ = {"schema": "crm"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)
    zip_code = Column(String(10), nullable=True)

    lead_source_id = Column(UUID(as_uuid=True), ForeignKey("crm.lead_sources.id"), nullable=False)
    lead_status = Column(String(50), nullable=False, server_default="new")  # new, contacted, qualified, converted, lost
    lead_score = Column(Integer, nullable=False, server_default="0")

    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    program_interest_id = Column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=True)
    converted_to_application_id = Column(UUID(as_uuid=True), nullable=True)

    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    lead_source = relationship("LeadSource", back_populates="leads")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    program_interest = relationship("Program", foreign_keys=[program_interest_id])
    custom_fields = relationship("LeadCustomField", back_populates="lead", cascade="all, delete-orphan")


class LeadCustomField(Base):
    """Custom fields for leads - flexible key-value storage."""
    __tablename__ = "lead_custom_fields"
    __table_args__ = {"schema": "crm"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("crm.leads.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(100), nullable=False)
    field_value = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    lead = relationship("Lead", back_populates="custom_fields")
