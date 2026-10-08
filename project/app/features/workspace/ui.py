"""UI layer for Feature 2 (Productivity Workspace). Owned by Developer 2."""

import streamlit as st
from app.core.components import render_empty_state, render_header


def render() -> None:
    render_header(
        title="Productivity Workspace",
        subtitle="Scratchpad, task management, and mindful prompts in a unified workspace.",
        icon="📝",
    )
    render_empty_state(
        title="Productivity Workspace Placeholder",
        message="Assigned to Developer 2 on branch `feature/productivity-workspace`.",
        icon="📋",
    )