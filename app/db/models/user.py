from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base
from app.db.models.role import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(CITEXT, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    status = Column(String, server_default="active")

    roles = relationship("Role", secondary=UserRole.__table__, lazy="joined", backref="users")
