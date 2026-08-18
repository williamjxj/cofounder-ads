import unittest
from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.calendar import due_platforms, load_calendar


class DuePlatformsTest(unittest.TestCase):
    def test_daily_x_is_due_every_day(self):
        calendar = {
            "platforms": {
                "x": {"cadence": "daily", "enabled": True},
                "reddit": {"cadence": "weekly", "weekday": 0, "enabled": True},
            }
        }
        monday = date(2026, 8, 17)
        tuesday = date(2026, 8, 18)
        self.assertIn("x", due_platforms(calendar, monday))
        self.assertIn("x", due_platforms(calendar, tuesday))

    def test_weekly_reddit_only_on_configured_weekday(self):
        calendar = {
            "platforms": {
                "reddit": {"cadence": "weekly", "weekday": 0, "enabled": True},
            }
        }
        monday = date(2026, 8, 17)
        tuesday = date(2026, 8, 18)
        self.assertEqual(due_platforms(calendar, monday), ["reddit"])
        self.assertEqual(due_platforms(calendar, tuesday), [])

    def test_disabled_platform_is_never_due(self):
        calendar = {
            "platforms": {
                "x": {"cadence": "daily", "enabled": False},
            }
        }
        self.assertEqual(due_platforms(calendar, date(2026, 8, 18)), [])

    def test_load_calendar_reads_yaml_file(self):
        path = ROOT / "calendar.yml"
        data = load_calendar(path)
        self.assertIn("x", data["platforms"])
        self.assertTrue(data["platforms"]["x"]["enabled"])


if __name__ == "__main__":
    unittest.main()
