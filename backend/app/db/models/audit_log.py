"""
Audit Log model for HIPAA compliance tracking.

Stores all API access logs, particularly PHI access, for compliance auditing.
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Index
from sqlalchemy.sql import func
from app.db.base import Base
import uuid


class AuditLog(Base):
    """
    Audit log for tracking all API access (especially PHI access).

    HIPAA requires:
    - Who accessed the data (user_id, user_email)
    - What data was accessed (endpoint, method)
    - When it was accessed (timestamp)
    - From where (ip_address)
    - What happened (status_code, is_phi_access)
    """
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Who accessed
    user_id = Column(String, nullable=True, index=True)  # None for anonymous
    user_email = Column(String, nullable=True)

    # What was accessed
    method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE
    path = Column(String(500), nullable=False, index=True)
    endpoint = Column(String(200), nullable=True)  # Normalized endpoint

    # When
    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # From where
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    user_agent = Column(String(500), nullable=True)

    # What happened
    status_code = Column(Integer, nullable=False, index=True)
    duration_ms = Column(Integer, nullable=True)  # Request duration
    request_size = Column(Integer, nullable=True)  # Request body size
    response_size = Column(Integer, nullable=True)  # Response body size

    # PHI tracking (critical for HIPAA)
    is_phi_access = Column(Boolean, default=False, nullable=False, index=True)

    # Additional context
    error_message = Column(Text, nullable=True)  # For 4xx/5xx responses
    query_params = Column(Text, nullable=True)  # Sanitized query parameters

    # Indexes for common queries
    __table_args__ = (
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_phi_timestamp', 'is_phi_access', 'timestamp'),
        Index('idx_audit_status_timestamp', 'status_code', 'timestamp'),
    )

    def __repr__(self):
        return (
            f"<AuditLog {self.method} {self.path} "
            f"by {self.user_email} at {self.timestamp}>"
        )
