"""Common utilities for time formatting, state, and execution safety."""

from datetime import datetime
import logging
from typing import Any, Callable, Optional
import streamlit as st


def setup_logger(name: str = "focusflow", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


logger = setup_logger()


def format_duration(seconds: int) -> str:
    """Format seconds into MM:SS or HH:MM:SS."""
    if seconds < 0:
        seconds = 0
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_timestamp(dt: Optional[datetime] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    target_dt = dt or datetime.now()
    return target_dt.strftime(fmt)


def init_session_state(key: str, default_value: Any) -> Any:
    if key not in st.session_state:
        st.session_state[key] = default_value
    return st.session_state[key]


def get_session_state(key: str, default: Any = None) -> Any:
    return st.session_state.get(key, default)


def set_session_state(key: str, value: Any) -> None:
    st.session_state[key] = value


def safe_execute(
    func: Callable[..., Any],
    *args: Any,
    fallback: Any = None,
    error_message: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    try:
        return func(*args, **kwargs)
    except Exception as exc:
        msg = error_message or f"Error executing {getattr(func, '__name__', str(func))}"
        logger.error(f"{msg}: {exc}", exc_info=True)
        return fallback