import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.dedupe import is_near_duplicate


class DedupeTest(unittest.TestCase):
    def test_identical_text_is_duplicate(self):
        text = "I ship AI apps 0-1. Looking for a business co-founder."
        self.assertTrue(is_near_duplicate(text, [text]))

    def test_unrelated_text_is_not_duplicate(self):
        self.assertFalse(
            is_near_duplicate(
                "You sell, I build. Fit call in the bio.",
                ["The weather in Portland is nice today."],
            )
        )

    def test_empty_history_is_never_duplicate(self):
        self.assertFalse(is_near_duplicate("anything", []))


if __name__ == "__main__":
    unittest.main()
