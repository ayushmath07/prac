"""Shared database infrastructure for SQLite and SQLAlchemy."""

from contextlib import contextmanager
import logging
from pathlib import Path
import sqlite3
from typing import Any, Generator, Optional

from app.core.config import get_config

logger = logging.getLogger("focusflow.database")

try:
    from sqlalchemy import create_engine as sa_create_engine, text as sa_text
    from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session, Session
    _HAS_SQLALCHEMY = True
except ImportError:
    _HAS_SQLALCHEMY = False


if _HAS_SQLALCHEMY:
    Base = declarative_base()

    def create_database_engine(database_url: Optional[str] = None):
        config = get_config()
        url = database_url or config.database_url

        if url.startswith("sqlite:///"):
            db_path = Path(url.replace("sqlite:///", ""))
            db_path.parent.mkdir(parents=True, exist_ok=True)

        return sa_create_engine(
            url,
            connect_args={"check_same_thread": False},
            echo=False,
            future=True,
        )

    _engine = create_database_engine()
    _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    SessionLocal = scoped_session(_session_factory)

    def get_engine():
        global _engine
        return _engine

    def init_db(engine=None) -> bool:
        target_engine = engine or get_engine()
        config = get_config()
        config.data_dir.mkdir(parents=True, exist_ok=True)
        Base.metadata.create_all(bind=target_engine)
        return True

    def check_db_connection(engine=None) -> bool:
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

else:
    class _BaseMeta:
        def __init__(self):
            self.tables = {}

        def create_all(self, bind=None):
            config = get_config()
            config.data_dir.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(config.db_file), check_same_thread=False)
            conn.close()

    class _BaseModel:
        metadata = _BaseMeta()

    Base = _BaseModel

    class _SQLiteShimSession:
        def __init__(self, db_path: Path):
            self.db_path = db_path
            self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._active = True

        def execute(self, statement: Any, params: Any = None):
            sql_text = str(statement)
            cursor = self._conn.cursor()
            if params:
                cursor.execute(sql_text, params)
            else:
                cursor.execute(sql_text)
            return cursor

        def commit(self):
            if self._active:
                self._conn.commit()

        def rollback(self):
            if self._active:
                self._conn.rollback()

        def close(self):
            if self._active:
                self._conn.close()
                self._active = False

    def init_db(engine=None) -> bool:
        config = get_config()
        config.data_dir.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(config.db_file), check_same_thread=False)
        conn.close()
        return True

    def check_db_connection(engine=None) -> bool:
        config = get_config()
        try:
            config.data_dir.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(config.db_file), check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            res = cursor.fetchone()
            conn.close()
            return res[0] == 1
        except Exception:
            return False

    @contextmanager
    def get_db_session() -> Generator[Any, None, None]:
        config = get_config()
        config.data_dir.mkdir(parents=True, exist_ok=True)
        session = _SQLiteShimSession(config.db_file)
        try:
            yield session
            session.commit()
        except Exception as exc:
            session.rollback()
            raise
        finally:
            session.close()

    SessionLocal = get_db_session