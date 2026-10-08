"""UI presentation layer for Feature 1 (Focus Timer)."""

import time
import streamlit as st

from app.core.components import (
    render_alert,
    render_card,
    render_empty_state,
    render_header,
    render_section,
    render_status_badge,
)
from app.core.utils import (
    format_duration,
    format_timestamp,
    get_session_state,
    init_session_state,
    set_session_state,
)
from app.features.focus import service


def render() -> None:
    render_header(
        title="Focus Timer",
        subtitle="Distraction-free countdown intervals to maintain momentum and deep focus.",
        icon="⏱️",
    )

    presets = service.get_presets()
    default_preset = "Pomodoro (25m)"
    default_duration = presets[default_preset]

    init_session_state("focus_selected_preset", default_preset)
    init_session_state("focus_duration_seconds", default_duration)
    init_session_state("focus_remaining_seconds", default_duration)
    init_session_state("focus_is_running", False)
    init_session_state("focus_is_paused", False)
    init_session_state("focus_completed_banner", None)

    remaining = get_session_state("focus_remaining_seconds", default_duration)
    is_running = get_session_state("focus_is_running", False)
    initial_duration = get_session_state("focus_duration_seconds", default_duration)
    current_preset = get_session_state("focus_selected_preset", default_preset)

    if is_running and remaining <= 0:
        service.record_completed_session(current_preset, initial_duration)
        set_session_state("focus_is_running", False)
        set_session_state("focus_is_paused", False)
        set_session_state("focus_remaining_seconds", initial_duration)
        set_session_state("focus_completed_banner", f"🎉 Focus session '{current_preset}' completed and saved to history!")
        st.rerun()

    banner_msg = get_session_state("focus_completed_banner")
    if banner_msg:
        render_alert(banner_msg, alert_type="success")
        set_session_state("focus_completed_banner", None)

    col_timer, col_config = st.columns([3, 2], gap="large")

    with col_timer:
        render_section("Active Session")

        is_paused = get_session_state("focus_is_paused", False)
        if is_running:
            badge_html = render_status_badge("Running", status="success")
        elif is_paused:
            badge_html = render_status_badge("Paused", status="warning")
        else:
            badge_html = render_status_badge("Ready", status="info")

        time_str = format_duration(remaining)
        progress_val = max(0.0, min(1.0, 1.0 - (remaining / initial_duration))) if initial_duration > 0 else 0.0

        st.markdown(
            f"""
            <div class="focus-card" style="text-align: center; padding: 2.5rem 1.5rem;">
                <div style="margin-bottom: 0.5rem;">{badge_html}</div>
                <div style="font-size: 4rem; font-weight: 800; font-family: monospace; color: #f8fafc; letter-spacing: 2px;">
                    {time_str}
                </div>
                <div style="font-size: 0.9rem; color: #94a3b8; margin-top: 0.5rem;">
                    Target: {current_preset} ({format_duration(initial_duration)})
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.progress(progress_val)

        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])

        if not is_running and not is_paused:
            with btn_col1:
                if st.button("▶ Start", use_container_width=True, type="primary"):
                    set_session_state("focus_is_running", True)
                    set_session_state("focus_is_paused", False)
                    st.rerun()
            with btn_col2:
                st.button("↺ Reset", use_container_width=True, disabled=True)
        elif is_running:
            with btn_col1:
                if st.button("⏸ Pause", use_container_width=True):
                    set_session_state("focus_is_running", False)
                    set_session_state("focus_is_paused", True)
                    st.rerun()
            with btn_col2:
                if st.button("↺ Reset", use_container_width=True):
                    set_session_state("focus_is_running", False)
                    set_session_state("focus_is_paused", False)
                    set_session_state("focus_remaining_seconds", initial_duration)
                    st.rerun()
        elif is_paused:
            with btn_col1:
                if st.button("▶ Resume", use_container_width=True, type="primary"):
                    set_session_state("focus_is_running", True)
                    set_session_state("focus_is_paused", False)
                    st.rerun()
            with btn_col2:
                if st.button("↺ Reset", use_container_width=True):
                    set_session_state("focus_is_running", False)
                    set_session_state("focus_is_paused", False)
                    set_session_state("focus_remaining_seconds", initial_duration)
                    st.rerun()

    with col_config:
        render_section("Timer Configuration")

        preset_names = list(presets.keys()) + ["Custom Interval"]
        selected = st.selectbox(
            "Select Interval Preset",
            options=preset_names,
            index=0 if current_preset not in preset_names else preset_names.index(current_preset),
            disabled=is_running,
        )

        if selected == "Custom Interval":
            custom_mins = st.number_input(
                "Duration (minutes)",
                min_value=1,
                max_value=180,
                value=int(initial_duration // 60) if initial_duration >= 60 else 25,
                step=5,
                disabled=is_running,
            )
            custom_seconds = int(custom_mins * 60)
            if not is_running and not is_paused and (initial_duration != custom_seconds or current_preset != "Custom Interval"):
                set_session_state("focus_selected_preset", "Custom Interval")
                set_session_state("focus_duration_seconds", custom_seconds)
                set_session_state("focus_remaining_seconds", custom_seconds)
                st.rerun()
        else:
            preset_seconds = presets[selected]
            if not is_running and not is_paused and (selected != current_preset or initial_duration != preset_seconds):
                set_session_state("focus_selected_preset", selected)
                set_session_state("focus_duration_seconds", preset_seconds)
                set_session_state("focus_remaining_seconds", preset_seconds)
                st.rerun()

        stats = service.get_session_stats()
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        render_card(
            title="Today's Productivity",
            value=f"{stats['today_minutes']} min",
            description=f"{stats['today_sessions']} sessions completed today • {stats['total_sessions']} all-time",
            badge="Today",
            status="success",
        )

    st.markdown("<hr style='margin: 2rem 0; border-color: #334155;' />", unsafe_allow_html=True)
    render_section("Completed Session History")

    history = service.get_session_history(limit=8)
    if not history:
        render_empty_state(
            title="No Completed Sessions Yet",
            message="Start and complete a countdown interval to log your productivity history in SQLite.",
            icon="⏱️",
        )
    else:
        hist_cols = st.columns(min(len(history), 4))
        for idx, item in enumerate(history[:4]):
            with hist_cols[idx]:
                dur_str = format_duration(item["duration_seconds"])
                created = item["created_at"]
                time_disp = created.strftime("%Y-%m-%d %H:%M") if hasattr(created, "strftime") else str(created)[:16]
                render_card(
                    title=item["session_name"],
                    value=dur_str,
                    description=f"Completed: {time_disp}",
                    status="info",
                )

    if is_running and remaining > 0:
        time.sleep(1)
        set_session_state("focus_remaining_seconds", remaining - 1)
        st.rerun()