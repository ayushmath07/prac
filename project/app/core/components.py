"""Shared UI components and layout helpers."""

from typing import Callable, Optional
import streamlit as st


def render_header(title: str, subtitle: Optional[str] = None, icon: Optional[str] = None) -> None:
    icon_html = f"<span style='margin-right: 0.5rem;'>{icon}</span>" if icon else ""
    subtitle_html = f"<div class='focus-brand-subtitle'>{subtitle}</div>" if subtitle else ""
    html = f"""
    <div class="focus-brand-header">
        <h1 class="focus-brand-title">{icon_html}{title}</h1>
        {subtitle_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_status_badge(text: str, status: str = "info") -> str:
    valid_statuses = {"info", "success", "warning", "danger"}
    status_class = status if status in valid_statuses else "info"
    return f'<span class="focus-badge focus-badge-{status_class}">{text}</span>'


def render_card(
    title: str,
    value: Optional[str] = None,
    description: Optional[str] = None,
    badge: Optional[str] = None,
    status: str = "info",
) -> None:
    badge_html = f"<div style='float: right;'>{render_status_badge(badge, status)}</div>" if badge else ""
    metric_html = f"<div class='focus-card-metric'>{value}</div>" if value else ""
    desc_html = f"<div class='focus-card-body'>{description}</div>" if description else ""

    html = f"""
    <div class="focus-card">
        {badge_html}
        <div class="focus-card-title">{title}</div>
        {metric_html}
        {desc_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_empty_state(
    title: str,
    message: str,
    icon: str = "📭",
    action_label: Optional[str] = None,
    action_callback: Optional[Callable[[], None]] = None,
    key: Optional[str] = None,
) -> None:
    html = f"""
    <div class="focus-empty-state">
        <div class="focus-empty-icon">{icon}</div>
        <div class="focus-empty-title">{title}</div>
        <div class="focus-empty-text">{message}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    if action_label and action_callback:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(action_label, key=key, use_container_width=True):
                action_callback()


def render_error(title: str, message: str, details: Optional[str] = None) -> None:
    details_html = (
        f"<details style='margin-top: 0.5rem; color: #f87171;'><summary style='cursor: pointer;'>Details</summary><pre style='background: #1e1e2e; padding: 0.5rem; border-radius: 4px; overflow-x: auto;'>{details}</pre></details>"
        if details
        else ""
    )
    html = f"""
    <div class="focus-error-box">
        <div class="focus-error-title">⚠️ {title}</div>
        <div class="focus-error-message">{message}</div>
        {details_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)