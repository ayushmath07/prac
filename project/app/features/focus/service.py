"""Business logic, timer configuration, and persistence for Feature 1 (Focus Timer).

Owned exclusively by Developer 1 on branch `feature/focus-timer`.
"""

from datetime import datetime, date
import logging
from typing import Any, Dict, List, Optional

from app.core.database import get_db_session, _HAS_SQLALCHEMY
from app.core.utils import setup_logger
from app.features.focus.models import FocusSession

logger = setup_logger("focusflow.focus_service")

# Preset timer interval configurations (label -> seconds)
TIMER_PRESETS: Dict[str, int] = {
    "Pomodoro (25m)": 25 * 60,
    "Deep Work (50m)": 50 * 60,
    "Short Break (5m)": 5 * 60,
    "Long Break (15m)": 15 * 60,
}


def _ensure_tables_and_pragmas(session: Any) -> None:
    """Ensure SQLite pragmas and tables are ready for safe transactions."""
    try:
        session.execute("PRAGMA journal_mode = MEMORY;")
        session.execute("PRAGMA temp_store = MEMORY;")
        session.execute("PRAGMA synchronous = OFF;")
        session.execute(
            """
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                duration_seconds INTEGER NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 1,
                created_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP
            );
            """
        )
    except Exception as exc:
        logger.debug(f"Pragma/table init notice: {exc}")


def get_presets() -> Dict[str, int]:
    """Retrieve available timer preset options."""
    return dict(TIMER_PRESETS)


def record_completed_session(session_name: str, duration_seconds: int) -> Optional[FocusSession]:
    """Persist a completed focus session into SQLite."""
    now = datetime.utcnow()

    with get_db_session() as session:
        _ensure_tables_and_pragmas(session)

        if _HAS_SQLALCHEMY:
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
        else:
            session.execute(
                """
                INSERT INTO focus_sessions (session_name, duration_seconds, completed, created_at, completed_at)
                VALUES (?, ?, 1, ?, ?);
                """,
                (session_name, duration_seconds, now.isoformat(), now.isoformat()),
            )
            logger.info(f"Recorded focus session via SQL fallback: '{session_name}'")
            return FocusSession(
                session_name=session_name,
                duration_seconds=duration_seconds,
                completed=True,
                created_at=now,
                completed_at=now,
            )


def get_session_history(limit: int = 15) -> List[Dict[str, Any]]:
    """Retrieve recent completed focus sessions ordered by newest first."""
    history: List[Dict[str, Any]] = []

    try:
        with get_db_session() as session:
            _ensure_tables_and_pragmas(session)

            if _HAS_SQLALCHEMY:
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
            else:
                cursor = session.execute(
                    """
                    SELECT id, session_name, duration_seconds, created_at
                    FROM focus_sessions
                    WHERE completed = 1
                    ORDER BY id DESC
                    LIMIT ?;
                    """,
                    (limit,),
                )
                rows = cursor.fetchall()
                for row in rows:
                    history.append({
                        "id": row[0],
                        "session_name": row[1],
                        "duration_seconds": row[2],
                        "created_at": row[3],
                    })
    except Exception as exc:
        logger.error(f"Error fetching session history: {exc}")

    return history


def get_session_stats() -> Dict[str, Any]:
    """Calculate aggregated session stats (today's count, today's minutes, all-time count)."""
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
        if isinstance(created, datetime):
            c_date = created.date().isoformat()
        else:
            c_date = str(created)[:10]

        if c_date == today_str:
            stats["today_sessions"] += 1
            stats["today_minutes"] += h["duration_seconds"] // 60

    return stats