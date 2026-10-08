"""Main entry point and application shell."""

import sys
from pathlib import Path
import streamlit as st

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.core.config import get_config
from app.core.database import init_db
from app.core.navigation import get_feature_registry, render_sidebar_navigation
from app.core.components import render_error
from app.core.utils import setup_logger
from app.styles.theme import inject_custom_css

from app.features.focus import ui as focus_ui
from app.features.workspace import ui as workspace_ui

logger = setup_logger("focusflow.main")


def setup_application() -> None:
    config = get_config()
    st.set_page_config(
        page_title=config.page_title,
        page_icon=config.page_icon,
        layout=config.layout,
        initial_sidebar_state=config.initial_sidebar_state,
    )
    init_db()


def register_features() -> None:
    registry = get_feature_registry()
    if not registry.get_all():
        registry.register(
            id="focus",
            name="Focus Timer",
            icon="⏱️",
            description="Pomodoro and custom countdown intervals for deep work.",
            render_func=focus_ui.render,
        )
        registry.register(
            id="workspace",
            name="Productivity Workspace",
            icon="📝",
            description="Integrated scratchpad, task list, and mindful prompts.",
            render_func=workspace_ui.render,
        )


def render_footer() -> None:
    st.markdown(
        """
        <div style="margin-top: 4rem; padding-top: 1rem; border-top: 1px solid #1e293b; text-align: center; font-size: 0.8rem; color: #64748b;">
            FocusFlow • Local & Private Productivity Dashboard • Zero Cloud Tracking
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    setup_application()
    inject_custom_css()
    register_features()

    registry = get_feature_registry()
    active_feature = render_sidebar_navigation(registry)

    if active_feature:
        try:
            active_feature.render_func()
        except Exception as exc:
            logger.error(f"Error rendering feature '{active_feature.id}': {exc}", exc_info=True)
            render_error(
                title=f"Error Loading {active_feature.name}",
                message="An unexpected error occurred while rendering this feature module.",
                details=str(exc),
            )
    else:
        render_error(
            title="No Features Available",
            message="No feature modules are currently registered in the Core navigation.",
        )

    render_footer()


if __name__ == "__main__":
    main()