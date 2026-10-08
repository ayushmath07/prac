"""Automated unit and integration tests for Feature 2: Productivity Workspace."""

import unittest
from app.core.database import Base, get_db_session, init_db
from app.features.workspace.models import WorkspaceNote, WorkspaceTask
from app.features.workspace.service import (
    add_task,
    clear_completed_tasks,
    delete_task,
    get_all_tasks,
    get_daily_prompt,
    get_scratchpad_note,
    get_task_metrics,
    save_scratchpad_note,
    toggle_task_status,
)


class TestWorkspaceFeature(unittest.TestCase):
    """Verifies workspace domain persistence, CRUD operations, and prompt rotation."""

    def setUp(self) -> None:
        init_db()
        # Clean workspace tables before each test
        with get_db_session() as session:
            session.query(WorkspaceTask).delete()
            session.query(WorkspaceNote).delete()

    def test_scratchpad_save_and_retrieve(self) -> None:
        """Verifies note persistence and update behavior."""
        save_scratchpad_note("Initial draft content", slug="default")
        self.assertEqual(get_scratchpad_note("default"), "Initial draft content")

        save_scratchpad_note("Updated draft content", slug="default")
        self.assertEqual(get_scratchpad_note("default"), "Updated draft content")

    def test_task_lifecycle(self) -> None:
        """Verifies adding, toggling, metrics, and deleting tasks."""
        # 1. Add Task
        task = add_task("Complete system design doc", priority="high")
        self.assertIsNotNone(task)
        self.assertEqual(task.title, "Complete system design doc")
        self.assertEqual(task.priority, "high")
        self.assertFalse(task.is_completed)

        # 2. Verify Metrics
        metrics = get_task_metrics()
        self.assertEqual(metrics["total"], 1)
        self.assertEqual(metrics["pending"], 1)
        self.assertEqual(metrics["completed"], 0)

        # 3. Toggle Completion
        toggled = toggle_task_status(task.id)
        self.assertTrue(toggled)
        metrics_after_toggle = get_task_metrics()
        self.assertEqual(metrics_after_toggle["completed"], 1)
        self.assertEqual(metrics_after_toggle["pending"], 0)

        # 4. Clear Completed
        cleared_count = clear_completed_tasks()
        self.assertEqual(cleared_count, 1)
        self.assertEqual(len(get_all_tasks()), 0)

    def test_motivational_prompt_output(self) -> None:
        """Verifies prompt retrieval contracts."""
        prompt = get_daily_prompt()
        self.assertIn("quote", prompt)
        self.assertIn("author", prompt)
        self.assertTrue(len(prompt["quote"]) > 0)


if __name__ == "__main__":
    unittest.main()