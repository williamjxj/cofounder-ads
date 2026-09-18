import tempfile
import unittest
from datetime import date
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.generate import ANGLES, X_BODIES, generate_linkedin, generate_reddit, generate_x
from engine.brief import load_brief
from engine.tick import run_tick
from engine.store import read_rows


def _sample_brief() -> dict:
    return load_brief(ROOT / "brief.md")


class GenerateXTest(unittest.TestCase):
    def test_x_post_fits_and_includes_cta(self):
        brief = _sample_brief()
        post = generate_x(brief, previous=[], on_date=date(2026, 8, 18))
        self.assertLessEqual(len(post["text"]), 280)
        self.assertIn(brief["cta_url"], post["text"])
        self.assertNotIn("investment", post["text"].lower())
        self.assertIn(post["angle"], ANGLES)

    def test_x_post_avoids_near_duplicate_history(self):
        brief = _sample_brief()
        first = generate_x(brief, previous=[], on_date=date(2026, 8, 17))
        second = generate_x(brief, previous=[first["text"]], on_date=date(2026, 8, 18))
        self.assertNotEqual(first["text"], second["text"])

    def test_x_bodies_fit_with_pages_cta(self):
        brief = _sample_brief()
        cta = brief["cta_url"]
        for angle, bodies in X_BODIES.items():
            for body in bodies:
                text = f"{body} {cta}"
                self.assertLessEqual(len(text), 280, f"{angle}: {len(text)} {body}")

    def test_spent_pool_uses_least_similar_not_first_only(self):
        brief = _sample_brief()
        previous = []
        seen = set()
        for i in range(40):
            post = generate_x(brief, previous=previous, on_date=date(2026, 1, 1 + (i % 28)))
            previous.append(post["text"])
            seen.add(post["text"])
        self.assertGreater(len(seen), 8)


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

    def test_reddit_varies_body_when_history_matches(self):
        brief = _sample_brief()
        first = generate_reddit(brief, previous_subs=[], on_date=date(2026, 8, 17))
        second = generate_reddit(
            brief,
            previous_subs=["indiehackers", "cofounder"],
            on_date=date(2026, 8, 17),
            previous_texts=[first["title"] + "\n" + first["body"]],
        )
        self.assertEqual(second["sub"], "startups")


class GenerateLinkedInTest(unittest.TestCase):
    def test_linkedin_includes_cta_and_stays_bounded(self):
        brief = _sample_brief()
        post = generate_linkedin(brief, previous=[], on_date=date(2026, 8, 20))
        self.assertIn(brief["cta_url"], post["text"])
        self.assertLessEqual(post["chars"], 1300)
        self.assertEqual(post["angle"], "hire")


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
        brief_path = self.tmp / "brief.md"
        text = brief_path.read_text(encoding="utf-8")
        brief_path.write_text(
            text.replace('x_handle: ""', 'x_handle: "wj"'), encoding="utf-8"
        )
        run_tick(self.tmp, on_date=date(2026, 8, 18))
        x_path = self.tmp / "queue" / "2026-08-18" / "x.md"
        self.assertIn("posting as @wj", x_path.read_text(encoding="utf-8"))

    def test_tick_on_monday_queues_x_and_reddit(self):
        result = run_tick(self.tmp, on_date=date(2026, 8, 17))
        self.assertEqual(result["platforms"], ["x", "reddit"])
        self.assertTrue((self.tmp / "queue" / "2026-08-17" / "reddit.md").exists())

    def test_tick_on_thursday_queues_x_and_linkedin(self):
        result = run_tick(self.tmp, on_date=date(2026, 8, 20))
        self.assertEqual(result["platforms"], ["x", "linkedin"])
        self.assertTrue((self.tmp / "queue" / "2026-08-20" / "linkedin.md").exists())

    def test_tick_is_idempotent_for_the_same_date(self):
        run_tick(self.tmp, on_date=date(2026, 8, 18))
        second = run_tick(self.tmp, on_date=date(2026, 8, 18))
        self.assertEqual(second["platforms"], [])
        self.assertEqual(second["skipped"], ["x"])
        rows = [r for r in read_rows(self.tmp / "ledger.csv") if r["platform"] == "x"]
        self.assertEqual(len(rows), 1)


if __name__ == "__main__":
    unittest.main()
