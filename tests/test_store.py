import unittest
from datetime import date
from pathlib import Path
import tempfile
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.tick import log_reply, mark_published, run_tick
from engine.store import read_rows


class PublishedAndCrmTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for name in ("brief.md", "calendar.yml"):
            shutil.copy(ROOT / name, self.tmp / name)
        shutil.copytree(ROOT / "platforms", self.tmp / "platforms")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_published_updates_queued_row(self):
        run_tick(self.tmp, on_date=date(2026, 8, 18))
        ok = mark_published(self.tmp, "x", "https://x.com/w/status/1")
        self.assertTrue(ok)
        rows = read_rows(self.tmp / "ledger.csv")
        x_rows = [r for r in rows if r["platform"] == "x"]
        self.assertEqual(x_rows[-1]["status"], "published")
        self.assertEqual(x_rows[-1]["url"], "https://x.com/w/status/1")

    def test_reply_appends_crm_row(self):
        log_reply(self.tmp, "x", "@alex", "asked about equity", "https://x.com/i/status/1")
        rows = read_rows(self.tmp / "crm.csv")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["from_handle"], "@alex")
        self.assertEqual(rows[0]["platform"], "x")


if __name__ == "__main__":
    unittest.main()
