"""Unit tests for Feature 1 (Focus Timer)."""

from pathlib import Path
import sys
import unittest

_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from app.core.database import init_db, get_db_session
from app.features.focus import service
from app.features.focus.models import FocusSession
from app.features.focus import ui as focus_ui


class TestFocusFeature(unittest.TestCase):
    """Test suite verifying Focus Timer models, services, and UI entry point."""

    def setUp(self):
        init_db()

    def test_presets_configuration(self):
        """Verify standard presets exist with positive seconds."""
        presets = service.get_presets()
        self.assertIn("Pomodoro (25m)", presets)
        self.assertEqual(presets["Pomodoro (25m)"], 1500)
        self.assertIn("Short Break (5m)", presets)
        self.assertEqual(presets["Short Break (5m)"], 300)

        for name, duration in presets.items():
            self.assertGreater(duration, 0)

    def test_record_and_retrieve_session(self):
        """Verify recording a completed focus session and retrieving history."""
        session_name = "Unit Test Focus Session"
        duration = 1500

        record = service.record_completed_session(session_name, duration)
        self.assertIsNotNone(record)

        history = service.get_session_history(limit=5)
        self.assertTrue(len(history) > 0)

        # Newest session should match
        latest = history[0]
        self.assertEqual(latest["session_name"], session_name)
        self.assertEqual(latest["duration_seconds"], duration)

    def test_session_statistics(self):
        """Verify calculation of daily and total session statistics."""
        service.record_completed_session("Stats Test Session", 1800)
        stats = service.get_session_stats()

        self.assertIn("today_sessions", stats)
        self.assertIn("today_minutes", stats)
        self.assertIn("total_sessions", stats)
        self.assertGreaterEqual(stats["total_sessions"], 1)
        self.assertGreaterEqual(stats["total_minutes"], 30)

    def test_ui_render_contract(self):
        """Verify UI render entry point executes safely."""
        try:
            focus_ui.render()
        except Exception as exc:
            self.fail(f"focus_ui.render() raised an unexpected exception: {exc}")


if __name__ == "__main__":
    unittest.main()