"""Application configuration and environment settings."""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = BASE_DIR / "database"
DEFAULT_DB_FILE = DATA_DIR / "app.db"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_FILE.as_posix()}")


@dataclass(frozen=True)
class AppConfig:
    app_name: str = "FocusFlow"
    app_tagline: str = "Single-Surface Local Productivity Dashboard"
    app_version: str = "0.1.0"

    base_dir: Path = BASE_DIR
    app_dir: Path = APP_DIR
    data_dir: Path = DATA_DIR
    db_file: Path = DEFAULT_DB_FILE
    database_url: str = DATABASE_URL

    page_title: str = "FocusFlow | Dashboard"
    page_icon: str = "⚡"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"
    default_feature: str = "focus"


_config_instance: Optional[AppConfig] = None


def get_config() -> AppConfig:
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig()
    return _config_instance