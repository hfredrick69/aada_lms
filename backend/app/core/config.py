import os
from pydantic import BaseModel


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
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        )
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


settings = Settings()
