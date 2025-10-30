import os
from pydantic import BaseModel

class Settings(BaseModel):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://aada:changeme@localhost:5432/aada_lms")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change_me")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    REFUND_DAYS_LIMIT: int = int(os.getenv("REFUND_DAYS_LIMIT", "45"))
    CANCELLATION_WINDOW_HOURS: int = int(os.getenv("CANCELLATION_WINDOW_HOURS", "72"))
    PROGRESS_REFUND_THRESHOLD: int = int(os.getenv("PROGRESS_REFUND_THRESHOLD", "50"))

settings = Settings()
