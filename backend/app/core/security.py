from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import re
import secrets
import hashlib
import uuid

import jwt
import bcrypt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings

# Use bcrypt for HIPAA-compliant password hashing
# Note: We use bcrypt directly for hash/verify to avoid passlib version detection bug
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def validate_password_strength(password: str) -> None:
    """
    Validate password meets HIPAA/NIST SP 800-63B requirements.

    Requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Raises HTTPException if password doesn't meet requirements.
    """
    errors = []

    if len(password) < settings.PASSWORD_MIN_LENGTH:
        errors.append(f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long")

    if settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")

    if settings.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")

    if settings.PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")

    if settings.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")

    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password does not meet security requirements", "errors": errors}
        )


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token with configurable expiration."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify JWT token."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash using bcrypt directly (avoids passlib bug)."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except (ValueError, AttributeError):
        return False


def get_password_hash(password: str) -> str:
    """
    Hash password using bcrypt after validating strength.

    Validates password meets security policy before hashing.
    Uses bcrypt directly to avoid passlib version detection bug.
    """
    validate_password_strength(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def hash_token(token: str) -> str:
    """Hash a token using SHA-256 for secure database storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def create_refresh_token(
    user_id: uuid.UUID,
    db: Session,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> str:
    """
    Create a new refresh token and store it in the database.

    Args:
        user_id: UUID of the user
        db: Database session
        ip_address: Client IP address for security tracking
        user_agent: Client user agent for device tracking

    Returns:
        The raw refresh token (send to client, hash is stored in DB)
    """
    from app.db.models.refresh_token import RefreshToken

    # Generate cryptographically secure random token
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)

    # Create database record
    refresh_token = RefreshToken(
        id=uuid.uuid4(),
        token_hash=token_hash,
        user_id=user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        ip_address=ip_address,
        user_agent=user_agent,
        use_count=0
    )

    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)

    return raw_token


def verify_refresh_token(token: str, db: Session) -> Optional[uuid.UUID]:
    """
    Verify a refresh token and return the user_id if valid.

    Args:
        token: The raw refresh token from client
        db: Database session

    Returns:
        User UUID if token is valid, None otherwise

    Raises:
        HTTPException if token is invalid, expired, or revoked
    """
    from app.db.models.refresh_token import RefreshToken

    token_hash = hash_token(token)

    # Find token in database
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).first()

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Check if revoked
    if refresh_token.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked"
        )

    # Check if expired
    if refresh_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )

    # Update last used timestamp and increment use count
    refresh_token.last_used_at = datetime.now(timezone.utc)
    refresh_token.use_count = int(refresh_token.use_count) + 1
    db.commit()

    return refresh_token.user_id


def revoke_refresh_token(
    token: str,
    db: Session,
    reason: Optional[str] = None
) -> None:
    """
    Revoke a specific refresh token.

    Args:
        token: The raw refresh token to revoke
        db: Database session
        reason: Optional reason for revocation (e.g., "logout", "password_change")
    """
    from app.db.models.refresh_token import RefreshToken

    token_hash = hash_token(token)

    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).first()

    if refresh_token and not refresh_token.is_revoked:
        refresh_token.is_revoked = True
        refresh_token.revoked_at = datetime.now(timezone.utc)
        refresh_token.revoke_reason = reason
        db.commit()


def revoke_all_user_tokens(
    user_id: uuid.UUID,
    db: Session,
    reason: Optional[str] = None
) -> int:
    """
    Revoke all refresh tokens for a user.

    Useful for password changes, account lockout, or security incidents.

    Args:
        user_id: UUID of the user
        db: Database session
        reason: Reason for revocation

    Returns:
        Number of tokens revoked
    """
    from app.db.models.refresh_token import RefreshToken

    count = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked == False  # noqa: E712
    ).update({
        "is_revoked": True,
        "revoked_at": datetime.now(timezone.utc),
        "revoke_reason": reason
    }, synchronize_session=False)

    db.commit()
    return count
