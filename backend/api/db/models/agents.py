from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String

from api.db.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("hosts.id"), unique=True, nullable=False)
    agent_key = Column(String(64), unique=True, index=True, nullable=False)
    token_hash = Column(String(128), nullable=False)
    hostname = Column(String(255), nullable=True)
    version = Column(String(64), nullable=True)
    docker_version = Column(String(64), nullable=True)
    capabilities = Column(JSON, nullable=True)
    last_heartbeat = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
