from sqlalchemy import Column, String, Boolean, DateTime
from api.db.database import Base


class SecretKey(Base):
    __tablename__ = "secret_key"
    key = Column(String, primary_key=True, index=True)


class TokenBlacklist(Base):
    __tablename__ = "jwt_token_blacklist"
    jti = Column(String, primary_key=True, index=True)
    expires = Column(DateTime, nullable=True)
    revoked = Column(Boolean, nullable=False)
