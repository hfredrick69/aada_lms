from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base
from app.db.models.role import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Encrypted fields use Text (base64-encoded ciphertext)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    status = Column(String, server_default="active")

    roles = relationship("Role", secondary=UserRole.__table__, lazy="joined", backref="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    signed_documents = relationship("SignedDocument", back_populates="user", cascade="all, delete-orphan")
