import tempfile
import unittest
from datetime import date
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.generate import generate_reddit, generate_x
from engine.brief import load_brief


def _sample_brief() -> dict:
    return load_brief(ROOT / "brief.md")


class GenerateXTest(unittest.TestCase):
    def test_x_post_fits_and_includes_cta(self):
        brief = _sample_brief()
        post = generate_x(brief, previous=[], on_date=date(2026, 8, 18))
        self.assertLessEqual(len(post["text"]), 280)
        self.assertIn(brief["cta_url"], post["text"])
        self.assertNotIn("investment", post["text"].lower())
        self.assertIn(post["angle"], ("ask", "proof", "split", "filter"))

    def test_x_post_avoids_near_duplicate_history(self):
        brief = _sample_brief()
        first = generate_x(brief, previous=[], on_date=date(2026, 8, 17))
        second = generate_x(brief, previous=[first["text"]], on_date=date(2026, 8, 18))
        self.assertNotEqual(first["text"], second["text"])


class GenerateRedditTest(unittest.TestCase):
    def test_reddit_has_title_body_and_rotating_sub(self):
        brief = _sample_brief()
        post = generate_reddit(brief, previous_subs=[], on_date=date(2026, 8, 17))
        self.assertTrue(post["title"])
        self.assertIn(brief["cta_url"], post["body"])
        self.assertIn(post["sub"], ("cofounder", "startups", "indiehackers"))
        self.assertNotEqual(post["title"], post["body"])

    def test_reddit_skips_last_used_sub(self):
        brief = _sample_brief()
        post = generate_reddit(
            brief, previous_subs=["cofounder"], on_date=date(2026, 8, 17)
        )
        self.assertNotEqual(post["sub"], "cofounder")

    def test_reddit_uses_cta_label_as_markdown_link(self):
        brief = _sample_brief()
        brief["cta_url"] = "https://cal.com/william/20min"
        brief["cta_label"] = "20-minute fit call"
        post = generate_reddit(brief, previous_subs=[], on_date=date(2026, 8, 17))
        self.assertIn("[20-minute fit call](https://cal.com/william/20min)", post["body"])

    def test_reddit_signs_off_with_author_name(self):
        brief = _sample_brief()
        brief["author_name"] = "William"
        post = generate_reddit(brief, previous_subs=[], on_date=date(2026, 8, 17))
        self.assertTrue(post["body"].strip().endswith("— William"))

    def test_reddit_falls_back_to_raw_url_without_label(self):
        brief = _sample_brief()
        brief["cta_url"] = "https://cal.com/william/20min"
        brief.pop("cta_label", None)
        post = generate_reddit(brief, previous_subs=[], on_date=date(2026, 8, 17))
        self.assertIn("https://cal.com/william/20min", post["body"])


class TickTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for name in ("brief.md", "calendar.yml"):
            shutil.copy(ROOT / name, self.tmp / name)
        shutil.copytree(ROOT / "platforms", self.tmp / "platforms")
        (self.tmp / "engine").mkdir()
        shutil.copy(ROOT / "engine" / "__init__.py", self.tmp / "engine" / "__init__.py")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_tick_on_tuesday_queues_x_only(self):
        from engine.tick import run_tick

        result = run_tick(self.tmp, on_date=date(2026, 8, 18))
        self.assertEqual(result["platforms"], ["x"])
        x_path = self.tmp / "queue" / "2026-08-18" / "x.md"
        digest = self.tmp / "queue" / "2026-08-18" / "APPROVE.md"
        self.assertTrue(x_path.exists())
        self.assertTrue(digest.exists())
        self.assertIn("Post", x_path.read_text(encoding="utf-8"))
        self.assertIn("x", digest.read_text(encoding="utf-8"))
        ledger = (self.tmp / "ledger.csv").read_text(encoding="utf-8")
        self.assertIn("queued", ledger)
        self.assertIn(",x,", ledger)

    def test_x_markdown_includes_handle_when_set(self):
        from engine.tick import run_tick

        brief_path = self.tmp / "brief.md"
        text = brief_path.read_text(encoding="utf-8")
        brief_path.write_text(
            text.replace('x_handle: ""', 'x_handle: "wj"'), encoding="utf-8"
        )
        run_tick(self.tmp, on_date=date(2026, 8, 18))
        x_path = self.tmp / "queue" / "2026-08-18" / "x.md"
        self.assertIn("posting as @wj", x_path.read_text(encoding="utf-8"))

    def test_tick_on_monday_queues_x_and_reddit(self):
        from engine.tick import run_tick

        result = run_tick(self.tmp, on_date=date(2026, 8, 17))
        self.assertEqual(result["platforms"], ["x", "reddit"])
        self.assertTrue((self.tmp / "queue" / "2026-08-17" / "reddit.md").exists())


if __name__ == "__main__":
    unittest.main()
