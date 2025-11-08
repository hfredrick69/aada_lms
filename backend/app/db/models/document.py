"""
Document and E-Signature Models

For managing enrollment agreements and other signed documents
with full audit trail for legal compliance.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class DocumentTemplate(Base):
    """Document templates (e.g., enrollment agreement)"""
    __tablename__ = "document_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)  # e.g., "Enrollment Agreement"
    description = Column(Text, nullable=True)
    version = Column(String(50), nullable=False)  # e.g., "v2.0"
    file_path = Column(String(500), nullable=False)  # Path to PDF template
    is_active = Column(Boolean, default=True)
    requires_counter_signature = Column(Boolean, default=False)  # School official signature

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document_instances = relationship("SignedDocument", back_populates="template")


class SignedDocument(Base):
    """Instance of a document sent to/signed by a student or lead"""
    __tablename__ = "signed_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("document_templates.id"), nullable=False)

    # Link to either a user (student) OR a lead (applicant)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("crm.leads.id"), nullable=True)

    # For leads without accounts, store signer info
    signer_name = Column(String(255), nullable=True)
    signer_email = Column(String(255), nullable=True)

    # Unique token for public signing (no login required)
    signing_token = Column(String(255), unique=True, nullable=True, index=True)
    token_expires_at = Column(DateTime, nullable=True)

    # Document status workflow
    status = Column(String(50), nullable=False, default="pending")
    # pending -> student_signed -> completed (if no counter-sig) or counter_signed -> completed

    # File paths
    unsigned_file_path = Column(String(500), nullable=True)  # Pre-filled PDF
    signed_file_path = Column(String(500), nullable=True)  # Final signed PDF

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    sent_at = Column(DateTime, nullable=True)  # When sent to student
    student_viewed_at = Column(DateTime, nullable=True)  # First view
    student_signed_at = Column(DateTime, nullable=True)
    counter_signed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    template = relationship("DocumentTemplate", back_populates="document_instances")
    user = relationship("User", back_populates="signed_documents")
    lead = relationship("Lead", back_populates="documents")
    signatures = relationship("DocumentSignature", back_populates="document", cascade="all, delete-orphan")
    audit_logs = relationship("DocumentAuditLog", back_populates="document", cascade="all, delete-orphan")


class DocumentSignature(Base):
    """Individual signatures on a document"""
    __tablename__ = "document_signatures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("signed_documents.id"), nullable=False)
    signer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Null for lead signatures

    signature_type = Column(String(50), nullable=False)  # "applicant", "student", or "school_official"
    signature_data = Column(Text, nullable=False)  # Base64 encoded signature image

    # Legal audit trail
    signed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String(45), nullable=False)  # IPv6 support
    user_agent = Column(Text, nullable=False)

    # Typed name and email (required for all signatures)
    typed_name = Column(String(255), nullable=False)
    signer_email = Column(String(255), nullable=True)  # For lead/applicant signatures

    # Relationships
    document = relationship("SignedDocument", back_populates="signatures")
    signer = relationship("User")


class DocumentAuditLog(Base):
    """Comprehensive audit trail for all document events"""
    __tablename__ = "document_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("signed_documents.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Null for system events

    event_type = Column(String(100), nullable=False)
    # Event types: created, sent, viewed, signed, counter_signed, completed, downloaded, etc.

    event_details = Column(Text, nullable=True)  # JSON string with additional context

    # Audit metadata
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Relationships
    document = relationship("SignedDocument", back_populates="audit_logs")
