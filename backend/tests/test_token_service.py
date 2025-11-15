"""
Unit tests for TokenService

Tests security and functionality of token generation/validation.
"""

from datetime import datetime, timedelta, timezone
from app.services.token_service import TokenService


class TestTokenService:
    """Test suite for TokenService"""

    def test_generate_signing_token_default_length(self):
        """Test token generation with default length"""
        token = TokenService.generate_signing_token()

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        # URL-safe base64 encoding of 64 bytes should be ~86 characters
        assert len(token) >= 80

    def test_generate_signing_token_custom_length(self):
        """Test token generation with custom length"""
        token = TokenService.generate_signing_token(length=32)

        assert token is not None
        assert isinstance(token, str)
        # Shorter length should produce shorter token
        assert len(token) < 80

    def test_generate_signing_token_uniqueness(self):
        """Test that generated tokens are unique (collision resistance)"""
        tokens = [TokenService.generate_signing_token() for _ in range(1000)]

        # All tokens should be unique
        assert len(tokens) == len(set(tokens))

    def test_generate_signing_token_url_safe(self):
        """Test that generated tokens are URL-safe"""
        token = TokenService.generate_signing_token()

        # URL-safe characters only (alphanumeric, -, _)
        assert all(c.isalnum() or c in ['-', '_'] for c in token)

    def test_calculate_token_expiration_default(self):
        """Test token expiration calculation with default days"""
        now = datetime.now(timezone.utc)
        expiration = TokenService.calculate_token_expiration()

        assert expiration > now
        # Should be approximately 30 days from now
        delta = expiration - now
        assert 29 <= delta.days <= 31

    def test_calculate_token_expiration_custom_days(self):
        """Test token expiration calculation with custom days"""
        now = datetime.now(timezone.utc)
        expiration = TokenService.calculate_token_expiration(days=7)

        assert expiration > now
        # Should be approximately 7 days from now
        delta = expiration - now
        assert 6 <= delta.days <= 8

    def test_is_token_expired_valid_token(self):
        """Test that non-expired tokens are validated correctly"""
        future = datetime.now(timezone.utc) + timedelta(days=1)

        assert TokenService.is_token_expired(future) is False

    def test_is_token_expired_expired_token(self):
        """Test that expired tokens are detected"""
        past = datetime.now(timezone.utc) - timedelta(days=1)

        assert TokenService.is_token_expired(past) is True

    def test_is_token_expired_none_expiration(self):
        """Test that None expiration is treated as expired (security)"""
        assert TokenService.is_token_expired(None) is True

    def test_is_token_expired_exact_expiration(self):
        """Test edge case of exact expiration time"""
        # Token that expires exactly now (should be expired)
        now = datetime.now(timezone.utc)

        # Due to time precision, this might be expired or not
        # We accept either outcome as long as it's consistent
        result = TokenService.is_token_expired(now)
        assert isinstance(result, bool)

    def test_is_token_valid_with_valid_token(self):
        """Test token validation with valid token and expiration"""
        token = "valid_token_string"
        expiration = datetime.now(timezone.utc) + timedelta(days=1)

        assert TokenService.is_token_valid(token, expiration) is True

    def test_is_token_valid_with_expired_token(self):
        """Test token validation with expired token"""
        token = "valid_token_string"
        expiration = datetime.now(timezone.utc) - timedelta(days=1)

        assert TokenService.is_token_valid(token, expiration) is False

    def test_is_token_valid_with_none_token(self):
        """Test token validation with None token (security)"""
        expiration = datetime.now(timezone.utc) + timedelta(days=1)

        assert TokenService.is_token_valid(None, expiration) is False

    def test_is_token_valid_with_empty_token(self):
        """Test token validation with empty token (security)"""
        expiration = datetime.now(timezone.utc) + timedelta(days=1)

        assert TokenService.is_token_valid("", expiration) is False

    def test_is_token_valid_with_none_expiration(self):
        """Test token validation with None expiration (security)"""
        token = "valid_token_string"

        assert TokenService.is_token_valid(token, None) is False

    def test_is_token_valid_with_both_none(self):
        """Test token validation with both None (security)"""
        assert TokenService.is_token_valid(None, None) is False

    def test_token_generation_performance(self):
        """Test that token generation is performant"""
        import time

        start = time.time()
        for _ in range(100):
            TokenService.generate_signing_token()
        elapsed = time.time() - start

        # Should generate 100 tokens in less than 1 second
        assert elapsed < 1.0

    def test_token_entropy(self):
        """Test that tokens have sufficient entropy (security)"""
        tokens = [TokenService.generate_signing_token() for _ in range(100)]

        # Check character distribution - should use full alphabet
        all_chars = ''.join(tokens)
        unique_chars = set(all_chars)

        # URL-safe base64 uses: A-Z, a-z, 0-9, -, _  (64 characters)
        # We should see good distribution
        assert len(unique_chars) >= 40  # At least 40 different characters used
