"""Navigation system and feature router."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
import streamlit as st

from app.core.config import get_config
from app.core.utils import get_session_state, set_session_state

NAV_STATE_KEY = "active_feature_id"


@dataclass
class FeatureItem:
    id: str
    name: str
    icon: str
    description: str
    render_func: Callable[[], Any]


class FeatureRegistry:
    def __init__(self):
        self._features: Dict[str, FeatureItem] = {}

    def register(
        self,
        id: str,
        name: str,
        icon: str,
        description: str,
        render_func: Callable[[], Any],
    ) -> None:
        self._features[id] = FeatureItem(
            id=id,
            name=name,
            icon=icon,
            description=description,
            render_func=render_func,
        )

    def get(self, id: str) -> Optional[FeatureItem]:
        return self._features.get(id)

    def get_all(self) -> List[FeatureItem]:
        return list(self._features.values())


_registry_instance: Optional[FeatureRegistry] = None


def get_feature_registry() -> FeatureRegistry:
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = FeatureRegistry()
    return _registry_instance


def get_active_feature_id(default_id: Optional[str] = None) -> str:
    config = get_config()
    fallback = default_id or config.default_feature
    return get_session_state(NAV_STATE_KEY, fallback)


def set_active_feature_id(feature_id: str) -> None:
    set_session_state(NAV_STATE_KEY, feature_id)


def render_sidebar_navigation(
    registry: FeatureRegistry,
    default_id: Optional[str] = None,
) -> Optional[FeatureItem]:
    config = get_config()
    features = registry.get_all()

    if not features:
        return None

    active_id = get_active_feature_id(default_id or features[0].id)
    feature_ids = [f.id for f in features]

    if active_id not in feature_ids:
        active_id = features[0].id
        set_active_feature_id(active_id)

    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding-top: 0.5rem; margin-bottom: 1.25rem;">
                <div class="sidebar-title">{config.page_icon} {config.app_name}</div>
                <div class="sidebar-version">v{config.app_version} • Local & Offline</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption("NAVIGATION")

        display_options = [f"{f.icon}  {f.name}" for f in features]
        id_to_index = {f.id: idx for idx, f in enumerate(features)}
        default_index = id_to_index.get(active_id, 0)

        selected_label = st.radio(
            "Select Feature",
            options=display_options,
            index=default_index,
            label_visibility="collapsed",
            key="sidebar_feature_radio",
        )

        selected_index = display_options.index(selected_label)
        selected_feature = features[selected_index]

        if selected_feature.id != active_id:
            set_active_feature_id(selected_feature.id)

        st.markdown("<hr style='margin: 1.5rem 0; border-color: #334155;' />", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="background-color: #1e293b; padding: 0.75rem; border-radius: 0.5rem; border: 1px solid #334155; font-size: 0.8rem; color: #94a3b8;">
                <div style="color: #10b981; font-weight: 600; margin-bottom: 0.25rem;">🔒 Offline & Private</div>
                All data stored locally in SQLite. Zero cloud tracking.
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected_feature