"""
Secure Token Generation Service

Generates cryptographically secure tokens for document signing.
Security features:
- Cryptographically random tokens (secrets module)
- Token expiration (configurable TTL)
- URL-safe encoding
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional


class TokenService:
    """Service for generating and validating secure signing tokens"""

    @staticmethod
    def generate_signing_token(length: int = 64) -> str:
        """
        Generate a cryptographically secure random token

        Args:
            length: Token length in bytes (default 64 = 512 bits)

        Returns:
            URL-safe token string

        Security:
            - Uses secrets.token_urlsafe() for cryptographic randomness
            - Default 512-bit entropy (NIST SP 800-57 recommendation)
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def calculate_token_expiration(days: int = 30) -> datetime:
        """
        Calculate token expiration time

        Args:
            days: Number of days until expiration (default 30)

        Returns:
            UTC datetime of expiration

        Security:
            - Default 30 days balances security vs usability
            - Configurable for different use cases
        """
        return datetime.now(timezone.utc) + timedelta(days=days)

    @staticmethod
    def is_token_expired(expires_at: Optional[datetime]) -> bool:
        """
        Check if a token has expired

        Args:
            expires_at: Expiration datetime (UTC)

        Returns:
            True if expired or missing, False if still valid

        Security:
            - Null-safe: missing expiration treated as expired
            - Uses UTC to avoid timezone attacks
        """
        if not expires_at:
            return True

        expires_at_utc = expires_at
        if expires_at_utc.tzinfo is None:
            expires_at_utc = expires_at_utc.replace(tzinfo=timezone.utc)

        return datetime.now(timezone.utc) > expires_at_utc

    @staticmethod
    def is_token_valid(token: Optional[str], expires_at: Optional[datetime]) -> bool:
        """
        Validate a token

        Args:
            token: Token string to validate
            expires_at: Token expiration datetime

        Returns:
            True if token exists and not expired

        Security:
            - Validates both presence and expiration
            - Constant-time comparison could be added for token matching
        """
        if not token:
            return False

        return not TokenService.is_token_expired(expires_at)
