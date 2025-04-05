from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from api.db.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(
        "email", String(length=264), unique=True, index=True, nullable=False
    )
    hashed_password = Column(String(length=72), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    keys = relationship("APIKEY", backref="user_key", cascade="all, delete-orphan")


class APIKEY(Base):
    __tablename__ = "apikeys"
    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String, index=True, nullable=False)
    jti = Column(String, unique=True, index=True, nullable=False)
    hashed_key = Column(String(length=72), unique=True, index=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime,
        nullable=False,
        unique=False,
        index=False,
        default=datetime.utcnow,
    )
    user = Column(Integer, ForeignKey("user.id"))
