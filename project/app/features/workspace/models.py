"""Database models for the Productivity Workspace feature."""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.core.database import Base


class WorkspaceNote(Base):
    """Stores local scratchpad notes with revision tracking."""

    __tablename__ = "workspace_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(50), unique=True, nullable=False, default="default")
    content = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<WorkspaceNote(slug='{self.slug}', updated_at='{self.updated_at}')>"


class WorkspaceTask(Base):
    """Stores todo tasks with priority, status, and completion time."""

    __tablename__ = "workspace_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    priority = Column(String(20), default="medium", nullable=False)  # low, medium, high
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<WorkspaceTask(id={self.id}, title='{self.title}', completed={self.is_completed})>"