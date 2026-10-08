"""Shared database infrastructure for SQLite and SQLAlchemy."""

from contextlib import contextmanager
import logging
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine as sa_create_engine, text as sa_text
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session, Session

from app.core.config import get_config

logger = logging.getLogger("focusflow.database")

Base = declarative_base()


def create_database_engine(database_url: Optional[str] = None):
    config = get_config()
    url = database_url or config.database_url

    if url.startswith("sqlite:///"):
        db_path = Path(url.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)

    return sa_create_engine(
        url,
        connect_args={"check_same_thread": False},  # Required for Streamlit concurrency
        echo=False,
        future=True,
    )


_engine = create_database_engine()
_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
SessionLocal = scoped_session(_session_factory)


def get_engine():
    return _engine


def init_db(engine=None) -> bool:
    """Initialize database tables registered on Base."""
    target_engine = engine or get_engine()
    config = get_config()
    config.data_dir.mkdir(parents=True, exist_ok=True)
    try:
        Base.metadata.create_all(bind=target_engine)
        logger.info("Database initialized successfully.")
        return True
    except Exception as exc:
        logger.error(f"Database initialization failed: {exc}", exc_info=True)
        raise


def check_db_connection(engine=None) -> bool:
    """Lightweight health check for SQLite connectivity."""
    target_engine = engine or get_engine()
    try:
        with target_engine.connect() as conn:
            result = conn.execute(sa_text("SELECT 1;")).scalar()
            return result == 1
    except Exception as exc:
        logger.error(f"Database health check failed: {exc}")
        return False


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager providing automatic transaction commit and rollback."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as exc:
        session.rollback()
        logger.error(f"Transaction rolled back: {exc}")
        raise
    finally:
        session.close()