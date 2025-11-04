"""
Refresh Token model for enhanced JWT security.

Implements token refresh pattern with:
- Short-lived access tokens (15 minutes)
- Long-lived refresh tokens (7 days)
- Token rotation on refresh
- Revocation support
"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid


class RefreshToken(Base):
    """
    Refresh tokens for JWT authentication.

    Security features:
    - Stored in database (not just JWT)
    - Single-use (rotated on each refresh)
    - Revocable (for logout/password change)
    - Tracks usage for attack detection
    """
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Token value (hashed for security)
    token_hash = Column(String, nullable=False, unique=True, index=True)

    # User relationship
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User", back_populates="refresh_tokens")

    # Token lifecycle
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Security tracking
    is_revoked = Column(Boolean, default=False, nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoke_reason = Column(String(200), nullable=True)

    # Device/session tracking
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Token rotation tracking (detect reuse attacks)
    replaced_by_token_id = Column(String, nullable=True)
    use_count = Column(String, default=0, nullable=False)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_refresh_user_active', 'user_id', 'is_revoked', 'expires_at'),
    )

    def __repr__(self):
        return (
            f"<RefreshToken {self.id[:8]} "
            f"for user {self.user_id[:8]} "
            f"expires {self.expires_at}>"
        )
