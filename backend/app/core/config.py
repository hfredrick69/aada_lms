import os
from pydantic import BaseModel, field_validator


class Settings(BaseModel):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://aada:changeme@localhost:5432/aada_lms"
    )

    # JWT/Authentication
    SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", os.getenv("SECRET_KEY", "change_me")
    )
    ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv(
            "JWT_EXPIRATION_MINUTES",
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
        )
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
    )

    # Password Policy (HIPAA/NIST compliant)
    PASSWORD_MIN_LENGTH: int = int(os.getenv("PASSWORD_MIN_LENGTH", "12"))
    PASSWORD_REQUIRE_UPPERCASE: bool = os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true"
    PASSWORD_REQUIRE_LOWERCASE: bool = os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true"
    PASSWORD_REQUIRE_DIGIT: bool = os.getenv("PASSWORD_REQUIRE_DIGIT", "true").lower() == "true"
    PASSWORD_REQUIRE_SPECIAL: bool = os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true"

    # Session Security
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    LOCKOUT_DURATION_MINUTES: int = int(os.getenv("LOCKOUT_DURATION_MINUTES", "30"))

    # Business Logic
    REFUND_DAYS_LIMIT: int = int(os.getenv("REFUND_DAYS_LIMIT", "45"))
    CANCELLATION_WINDOW_HOURS: int = int(os.getenv("CANCELLATION_WINDOW_HOURS", "72"))
    PROGRESS_REFUND_THRESHOLD: int = int(os.getenv("PROGRESS_REFUND_THRESHOLD", "50"))

    # Backend
    BACKEND_BASE_URL: str = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:5174")

    # CORS - comma-separated list of allowed origins
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174,"
        "https://localhost:5173,https://localhost:5174"
    )

    # Email / registration
    EMAIL_PROVIDER: str = os.getenv("EMAIL_PROVIDER", "console")
    SENDGRID_API_KEY: str | None = os.getenv("SENDGRID_API_KEY")
    SENDGRID_FROM_EMAIL: str = os.getenv("SENDGRID_FROM_EMAIL", "no-reply@aada.edu")
    ACS_CONNECTION_STRING: str | None = os.getenv("ACS_CONNECTION_STRING")
    ACS_SENDER_EMAIL: str = os.getenv("ACS_SENDER_EMAIL", "no-reply@aada.edu")
    REGISTRATION_EMAIL_EXPIRE_MINUTES: int = int(os.getenv("REGISTRATION_EMAIL_EXPIRE_MINUTES", "30"))
    REGISTRATION_COMPLETION_EXPIRE_MINUTES: int = int(os.getenv("REGISTRATION_COMPLETION_EXPIRE_MINUTES", "15"))

    # Encryption (PII/PHI encryption key)
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "change_this_key_in_production_32bytes")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate JWT secret key strength"""
        if not v or v == "change_me":
            raise ValueError(
                "JWT_SECRET_KEY must be set to a strong value. "
                "Generate with: python3 -c \"import secrets; print(secrets.token_urlsafe(64))\""
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters for security")
        return v

    @field_validator('ENCRYPTION_KEY')
    @classmethod
    def validate_encryption_key(cls, v: str) -> str:
        """Validate encryption key strength"""
        if not v or v.startswith("change_"):
            raise ValueError(
                "ENCRYPTION_KEY must be set from environment variables. "
                "Never use default values. "
                "Generate with: python3 -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        if len(v) < 32:
            raise ValueError("ENCRYPTION_KEY must be at least 32 characters for security")
        return v


settings = Settings()
