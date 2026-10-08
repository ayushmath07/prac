"""Shared styling and design system."""

import streamlit as st

CUSTOM_CSS = """
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
.focus-brand-header {
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}
.focus-brand-title {
    font-size: 2rem;
    font-weight: 700;
    color: #f8fafc;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
}
.focus-brand-subtitle {
    font-size: 0.95rem;
    color: #94a3b8;
    margin-top: 0.25rem;
}
.focus-card {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 0.75rem;
    padding: 1.25rem;
    margin-bottom: 1rem;
}
.focus-card-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #f8fafc;
    margin-bottom: 0.5rem;
}
.focus-card-body {
    font-size: 0.95rem;
    color: #cbd5e1;
    line-height: 1.5;
}
.focus-card-metric {
    font-size: 2.2rem;
    font-weight: 700;
    color: #6366f1;
    margin: 0.5rem 0;
}
.focus-badge {
    display: inline-block;
    padding: 0.25rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}
.focus-badge-info { background-color: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
.focus-badge-success { background-color: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
.focus-badge-warning { background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
.focus-badge-danger { background-color: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }

.focus-empty-state {
    text-align: center;
    padding: 3rem 1.5rem;
    background-color: rgba(30, 41, 59, 0.5);
    border: 2px dashed #334155;
    border-radius: 1rem;
    margin: 1.5rem 0;
}
.focus-empty-icon { font-size: 3rem; margin-bottom: 0.75rem; }
.focus-empty-title { font-size: 1.25rem; font-weight: 600; color: #f8fafc; margin-bottom: 0.25rem; }
.focus-empty-text { font-size: 0.9rem; color: #94a3b8; max-width: 400px; margin: 0 auto; }

.focus-error-box {
    background-color: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 0.75rem;
    padding: 1.25rem;
    margin: 1rem 0;
}
.focus-error-title { font-size: 1rem; font-weight: 600; color: #f87171; }
.focus-error-message { font-size: 0.875rem; color: #fca5a5; }

section[data-testid="stSidebar"] {
    background-color: #0b1120;
    border-right: 1px solid #1e293b;
}
.sidebar-title { font-size: 1.3rem; font-weight: 700; color: #f8fafc; margin-bottom: 0.25rem; }
.sidebar-version { font-size: 0.75rem; color: #64748b; margin-bottom: 1.5rem; }
</style>
"""


def inject_custom_css() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)