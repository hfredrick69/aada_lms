"""
Login Attempt Model

Tracks failed login attempts for brute-force protection.
"""
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone

from app.db.base import Base


class LoginAttempt(Base):
    """Track login attempts for rate limiting and security monitoring"""
    __tablename__ = "login_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_hash = Column(String(64), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    attempted_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    success = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return (
            f"<LoginAttempt(email_hash={self.email_hash[:8]}..., "
            f"success={self.success}, attempted_at={self.attempted_at})>"
        )
