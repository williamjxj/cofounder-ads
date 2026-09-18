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
from engine.status import collect_status

PAGES = "https://williamjxj.github.io/cofounder-ads/"


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
        brief_path = self.tmp / "brief.md"
        text = brief_path.read_text(encoding="utf-8")
        brief_path.write_text(
            text.replace(PAGES, "https://cal.com/william/20min"),
            encoding="utf-8",
        )
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


class CsvFallbackTest(unittest.TestCase):
    def test_read_rows_falls_back_when_supabase_raises(self):
        from unittest.mock import patch

        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(tmp))
        csv_path = tmp / "ledger.csv"
        csv_path.write_text("date,platform,status,angle,sub,chars,path,url,text\n2026-01-01,x,queued,,,,,,hi\n", encoding="utf-8")
        with patch("engine.store.supabase_store.enabled", return_value=True), patch(
            "engine.store.supabase_store.fetch_rows",
            side_effect=RuntimeError("network boom"),
        ):
            rows = read_rows(csv_path)
        self.assertEqual(rows[0]["text"], "hi")


class PublishGuardTest(unittest.TestCase):
    """mark_published must refuse placeholder URLs and unset cta_urls —
    this prevents the fake-published ledger row that happened on 2026-08-18."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for name in ("brief.md", "calendar.yml"):
            shutil.copy(ROOT / name, self.tmp / name)
        shutil.copytree(ROOT / "platforms", self.tmp / "platforms")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _write_brief_cta(self, cta: str):
        path = self.tmp / "brief.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace(PAGES, cta), encoding="utf-8")

    def test_published_refuses_placeholder_url(self):
        run_tick(self.tmp, on_date=date(2026, 8, 18))
        with self.assertRaises(ValueError):
            mark_published(self.tmp, "x", "https://x.com/YOU/status/ID")

    def test_published_refuses_when_cta_is_placeholder(self):
        self._write_brief_cta("REPLACE_ME")
        run_tick(self.tmp, on_date=date(2026, 8, 18))
        with self.assertRaises(ValueError):
            mark_published(self.tmp, "x", "https://x.com/real/status/1")

    def test_status_reports_real_cta(self):
        info = collect_status(ROOT, on_date=date(2026, 9, 17))
        self.assertTrue(info["cta_ok"])

    def test_published_allowed_with_real_cta_and_url(self):
        self._write_brief_cta("https://cal.com/william/20min")
        run_tick(self.tmp, on_date=date(2026, 8, 18))
        ok = mark_published(self.tmp, "x", "https://x.com/real/status/1")
        self.assertTrue(ok)
        rows = read_rows(self.tmp / "ledger.csv")
        x_rows = [r for r in rows if r["platform"] == "x"]
        self.assertEqual(x_rows[-1]["status"], "published")


if __name__ == "__main__":
    unittest.main()
