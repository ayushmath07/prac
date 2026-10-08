"""Presentation layer for the Productivity Workspace."""

import streamlit as st

from app.core.components import (
    render_card,
    render_empty_state,
    render_header,
    render_section,
    render_status_badge,
)
from app.core.utils import (
    format_timestamp,
    get_session_state,
    init_session_state,
    set_session_state,
)
from app.features.workspace.service import (
    add_task,
    clear_completed_tasks,
    delete_task,
    get_all_tasks,
    get_daily_prompt,
    get_random_prompt,
    get_scratchpad_note,
    get_task_metrics,
    save_scratchpad_note,
    toggle_task_status,
)


def _init_workspace_state() -> None:
    """Initializes isolated session state values for the workspace."""
    init_session_state("workspace_note_synced", False)
    if "workspace_active_prompt" not in st.session_state:
        set_session_state("workspace_active_prompt", get_daily_prompt())


def _render_mindfulness_banner() -> None:
    """Renders the rotating motivational quote card."""
    prompt = get_session_state("workspace_active_prompt", get_daily_prompt())

    col_quote, col_btn = st.columns([5, 1])
    with col_quote:
        st.markdown(
            f"""
            <div style="
                background: rgba(255, 255, 255, 0.03);
                border-left: 3px solid #6366f1;
                padding: 12px 18px;
                border-radius: 4px;
                margin-bottom: 1.2rem;
            ">
                <span style="font-size: 1.05rem; font-style: italic; color: #e2e8f0;">"{prompt['quote']}"</span>
                <span style="display: block; font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">— {prompt['author']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_btn:
        if st.button("🔄 New Prompt", key="workspace_new_prompt_btn", use_container_width=True):
            set_session_state("workspace_active_prompt", get_random_prompt())
            st.rerun()


def _render_metrics() -> None:
    """Renders quick status metric cards."""
    metrics = get_task_metrics()
    c1, c2, c3 = st.columns(3)
    with c1:
        render_card(
            title="Active Tasks",
            value=str(metrics["pending"]),
            description="Items needing attention",
            badge="Pending",
            status="info" if metrics["pending"] > 0 else "success",
        )
    with c2:
        render_card(
            title="Completed",
            value=str(metrics["completed"]),
            description="Finished milestones",
            badge="Done",
            status="success",
        )
    with c3:
        completion_rate = (
            f"{(metrics['completed'] / metrics['total']) * 100:.0f}%"
            if metrics["total"] > 0
            else "100%"
        )
        render_card(
            title="Task Completion",
            value=completion_rate,
            description="Total output velocity",
            badge="Ratio",
            status="info",
        )


def _render_scratchpad() -> None:
    """Renders the auto-saving scratchpad editor."""
    render_section(
        title="Quick Scratchpad",
        description="Local temporary storage for thoughts, code snippets, and reference text.",
    )

    current_text = get_scratchpad_note(slug="default")

    note_input = st.text_area(
        label="Scratchpad Area",
        value=current_text,
        height=320,
        placeholder="Type quick notes, scratchpad items, or thoughts here...",
        key="workspace_scratchpad_textarea",
        label_visibility="collapsed",
    )

    col_actions, col_status = st.columns([1, 4])
    with col_actions:
        if st.button("💾 Save Note", key="workspace_save_note_btn", use_container_width=True):
            save_scratchpad_note(note_input, slug="default")
            st.toast("Note saved to local database!", icon="✅")
            st.rerun()

    with col_status:
        char_count = len(note_input) if note_input else 0
        word_count = len(note_input.split()) if note_input else 0
        st.markdown(
            f"<div style='padding-top: 8px; font-size: 0.82rem; color: #64748b;'>"
            f"{char_count} characters | {word_count} words | Local SQLite"
            f"</div>",
            unsafe_allow_html=True,
        )


def _render_todo_list() -> None:
    """Renders the task list manager with create, toggle, and delete controls."""
    render_section(
        title="To-Do List",
        description="Track tasks, categorize by priority, and mark progress.",
    )

    # Task input form
    with st.form(key="workspace_add_task_form", clear_on_submit=True):
        f_col1, f_col2, f_col3 = st.columns([4, 1.5, 1])
        with f_col1:
            task_title = st.text_input(
                "Task title",
                placeholder="What needs to be done?",
                label_visibility="collapsed",
            )
        with f_col2:
            priority = st.selectbox(
                "Priority",
                options=["Medium", "High", "Low"],
                index=0,
                label_visibility="collapsed",
            )
        with f_col3:
            submitted = st.form_submit_button("Add Task", use_container_width=True)

        if submitted and task_title.strip():
            add_task(title=task_title, priority=priority)
            st.rerun()

    # Task items list
    tasks = get_all_tasks(include_completed=True)

    if not tasks:
        render_empty_state(
            title="No tasks on your board",
            message="Add your first action item using the input field above.",
            icon="📋",
        )
        return

    # Clear completed button if applicable
    has_completed = any(t.is_completed for t in tasks)
    if has_completed:
        _, right_col = st.columns([4, 1])
        with right_col:
            if st.button(
                "Clear Completed",
                key="workspace_clear_completed_btn",
                use_container_width=True,
            ):
                clear_completed_tasks()
                st.rerun()

    # Render each task row
    for task in tasks:
        row_col1, row_col2, row_col3, row_col4 = st.columns([0.6, 5, 1.2, 0.6])

        with row_col1:
            # Checkbox toggle
            is_checked = st.checkbox(
                label=f"toggle_{task.id}",
                value=task.is_completed,
                key=f"workspace_task_check_{task.id}",
                label_visibility="collapsed",
            )
            if is_checked != task.is_completed:
                toggle_task_status(task.id)
                st.rerun()

        with row_col2:
            title_display = (
                f"~~{task.title}~~" if task.is_completed else f"**{task.title}**"
            )
            st.markdown(
                f"<div style='padding-top: 4px;'>{title_display}</div>",
                unsafe_allow_html=True,
            )

        with row_col3:
            # Priority badge mapping
            status_map = {"high": "danger", "medium": "warning", "low": "info"}
            render_status_badge(
                text=task.priority.capitalize(),
                status=status_map.get(task.priority, "info"),
            )

        with row_col4:
            if st.button(
                "✕",
                key=f"workspace_del_{task.id}",
                help="Delete task",
                use_container_width=True,
            ):
                delete_task(task.id)
                st.rerun()


def render() -> None:
    """Main parameterless presentation entry point for the Productivity Workspace."""
    _init_workspace_state()

    render_header(
        title="Productivity Workspace",
        subtitle="Consolidated scratchpad, action items, and mindfulness",
        icon="📝",
    )

    _render_mindfulness_banner()
    _render_metrics()

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        _render_scratchpad()

    with col_right:
        _render_todo_list()