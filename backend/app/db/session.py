import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Optimized connection pool configuration
# pool_size: Number of permanent connections (20)
# max_overflow: Additional connections when pool exhausted (40)
# pool_timeout: Wait time before raising error (30s)
# pool_recycle: Recycle connections after 1 hour
# pool_pre_ping: Test connections before use
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    from sqlalchemy.orm import Session
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
