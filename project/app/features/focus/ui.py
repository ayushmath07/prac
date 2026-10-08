"""UI layer for Feature 1 (Focus Timer). Owned by Developer 1."""

import streamlit as st
from app.core.components import render_empty_state, render_header


def render() -> None:
    render_header(
        title="Focus Timer",
        subtitle="Customizable countdown intervals for distraction-free deep work sessions.",
        icon="⏱️",
    )
    render_empty_state(
        title="Focus Timer Feature Placeholder",
        message="Assigned to Developer 1 on branch `feature/focus-timer`.",
        icon="⏳",
    )