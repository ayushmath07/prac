"""Domain logic and database service layer for the Productivity Workspace."""

import random
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import desc

from app.core.database import get_db_session
from app.features.workspace.models import WorkspaceNote, WorkspaceTask

# --- Curated Mindful / Motivational Prompts ---
MOTIVATIONAL_PROMPTS: List[Dict[str, str]] = [
    {
        "quote": "Focus is a muscle. The more you protect your attention, the stronger it gets.",
        "author": "Deep Work Principle",
    },
    {
        "quote": "You do not rise to the level of your goals. You fall to the level of your systems.",
        "author": "James Clear",
    },
    {
        "quote": "It is not that we have a short time to live, but that we waste a lot of it.",
        "author": "Seneca",
    },
    {
        "quote": "Small disciplines repeated with consistency every day lead to great achievements gained slowly over time.",
        "author": "John C. Maxwell",
    },
    {
        "quote": "Do the hard jobs first. The easy jobs will take care of themselves.",
        "author": "Dale Carnegie",
    },
    {
        "quote": "Action isn't just the effect of motivation; it's also the cause of it.",
        "author": "Mark Manson",
    },
    {
        "quote": "Simplicity boils down to two steps: Identify the essential. Eliminate the rest.",
        "author": "Leo Babauta",
    },
]


# --- Motivational Prompt Service ---
def get_daily_prompt(seed: Optional[int] = None) -> Dict[str, str]:
    """Returns a deterministic daily prompt or a random one if requested."""
    if seed is not None:
        idx = seed % len(MOTIVATIONAL_PROMPTS)
        return MOTIVATIONAL_PROMPTS[idx]
    # Deterministic rotation based on calendar day of the year
    day_of_year = datetime.now().timetuple().tm_yday
    return MOTIVATIONAL_PROMPTS[day_of_year % len(MOTIVATIONAL_PROMPTS)]


def get_random_prompt() -> Dict[str, str]:
    """Fetches a random prompt on user request."""
    return random.choice(MOTIVATIONAL_PROMPTS)


# --- Scratchpad Note Services ---
def get_scratchpad_note(slug: str = "default") -> str:
    """Retrieves the scratchpad text content for a given slug."""
    with get_db_session() as session:
        note = session.query(WorkspaceNote).filter_by(slug=slug).first()
        return note.content if note else ""


def save_scratchpad_note(content: str, slug: str = "default") -> None:
    """Creates or updates the scratchpad note content."""
    with get_db_session() as session:
        note = session.query(WorkspaceNote).filter_by(slug=slug).first()
        if note:
            note.content = content
            note.updated_at = datetime.utcnow()
        else:
            note = WorkspaceNote(slug=slug, content=content)
            session.add(note)


# --- Task / To-Do List Services ---
def get_all_tasks(include_completed: bool = True) -> List[WorkspaceTask]:
    """Retrieves tasks ordered by completion status, priority, and creation time."""
    with get_db_session() as session:
        query = session.query(WorkspaceTask)
        if not include_completed:
            query = query.filter_by(is_completed=False)
        # Pending first, then by latest created
        return query.order_by(
            WorkspaceTask.is_completed.asc(),
            desc(WorkspaceTask.created_at)
        ).all()


def add_task(title: str, priority: str = "medium") -> Optional[WorkspaceTask]:
    """Adds a new task to the to-do list."""
    cleaned_title = title.strip()
    if not cleaned_title:
        return None

    with get_db_session() as session:
        task = WorkspaceTask(
            title=cleaned_title,
            priority=priority.lower(),
            is_completed=False,
            created_at=datetime.utcnow(),
        )
        session.add(task)
        session.flush()
        session.refresh(task)
        return task


def toggle_task_status(task_id: int) -> bool:
    """Toggles task status between active and completed."""
    with get_db_session() as session:
        task = session.query(WorkspaceTask).filter_by(id=task_id).first()
        if not task:
            return False

        task.is_completed = not task.is_completed
        task.completed_at = datetime.utcnow() if task.is_completed else None
        return True


def delete_task(task_id: int) -> bool:
    """Deletes a specific task by ID."""
    with get_db_session() as session:
        task = session.query(WorkspaceTask).filter_by(id=task_id).first()
        if not task:
            return False
        session.delete(task)
        return True


def clear_completed_tasks() -> int:
    """Removes all completed tasks from the database."""
    with get_db_session() as session:
        deleted = (
            session.query(WorkspaceTask)
            .filter_by(is_completed=True)
            .delete(synchronize_session="fetch")
        )
        return deleted


def get_task_metrics() -> Dict[str, int]:
    """Returns aggregate metrics for dashboard summaries."""
    with get_db_session() as session:
        total = session.query(WorkspaceTask).count()
        completed = session.query(WorkspaceTask).filter_by(is_completed=True).count()
        pending = total - completed
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
        }