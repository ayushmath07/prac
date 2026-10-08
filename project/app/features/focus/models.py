"""Database models for Feature 1 (Focus Timer)."""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from app.core.database import Base


class FocusSession(Base):
    """Model tracking completed focus intervals."""

    __tablename__ = "focus_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_name = Column(String(100), nullable=False, default="Focus Session")
    duration_seconds = Column(Integer, nullable=False, default=1500)
    completed = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    def __init__(
        self,
        session_name: str = "Focus Session",
        duration_seconds: int = 1500,
        completed: bool = True,
        created_at: datetime = None,
        completed_at: datetime = None,
        id: int = None,
    ):
        self.id = id
        self.session_name = session_name
        self.duration_seconds = duration_seconds
        self.completed = completed
        self.created_at = created_at or datetime.utcnow()
        self.completed_at = completed_at or datetime.utcnow()