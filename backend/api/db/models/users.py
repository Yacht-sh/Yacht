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

    # New fields for 2FA and Roles
    otp_secret = Column(String(length=32), nullable=True)
    is_2fa_enabled = Column(Boolean, default=False, nullable=False)
    # Storing permissions as boolean columns for explicit clarity as requested
    # "Restart, start, stop, remove/delete"
    perm_start = Column(Boolean, default=False)
    perm_stop = Column(Boolean, default=False)
    perm_restart = Column(Boolean, default=False)
    perm_delete = Column(Boolean, default=False)
    # roles field can be kept for future or generic roles like "admin" (which is is_superuser)
    roles = Column(String(length=512), default="", nullable=True)

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

class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, index=True)
    username = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean)
