"""Business logic, timer configuration, and persistence for Feature 1 (Focus Timer)."""

from datetime import datetime, date
import logging
from typing import Any, Dict, List, Optional

from app.core.database import get_db_session
from app.core.utils import setup_logger
from app.features.focus.models import FocusSession

logger = setup_logger("focusflow.focus_service")

TIMER_PRESETS: Dict[str, int] = {
    "Pomodoro (25m)": 25 * 60,
    "Deep Work (50m)": 50 * 60,
    "Short Break (5m)": 5 * 60,
    "Long Break (15m)": 15 * 60,
}


def get_presets() -> Dict[str, int]:
    return dict(TIMER_PRESETS)


def record_completed_session(session_name: str, duration_seconds: int) -> Optional[FocusSession]:
    now = datetime.utcnow()
    with get_db_session() as session:
        record = FocusSession(
            session_name=session_name,
            duration_seconds=duration_seconds,
            completed=True,
            created_at=now,
            completed_at=now,
        )
        session.add(record)
        logger.info(f"Recorded focus session: '{session_name}' ({duration_seconds}s)")
        return record


def get_session_history(limit: int = 15) -> List[Dict[str, Any]]:
    history: List[Dict[str, Any]] = []
    try:
        with get_db_session() as session:
            records = (
                session.query(FocusSession)
                .filter(FocusSession.completed == True)
                .order_by(FocusSession.created_at.desc())
                .limit(limit)
                .all()
            )
            for r in records:
                history.append({
                    "id": r.id,
                    "session_name": r.session_name,
                    "duration_seconds": r.duration_seconds,
                    "created_at": r.created_at,
                })
    except Exception as exc:
        logger.error(f"Error fetching session history: {exc}")
    return history


def get_session_stats() -> Dict[str, Any]:
    stats = {
        "today_sessions": 0,
        "today_minutes": 0,
        "total_sessions": 0,
        "total_minutes": 0,
    }
    history = get_session_history(limit=500)
    stats["total_sessions"] = len(history)
    stats["total_minutes"] = sum(h["duration_seconds"] for h in history) // 60

    today_str = date.today().isoformat()
    for h in history:
        created = h["created_at"]
        c_date = created.date().isoformat() if isinstance(created, datetime) else str(created)[:10]
        if c_date == today_str:
            stats["today_sessions"] += 1
            stats["today_minutes"] += h["duration_seconds"] // 60
    return stats