from __future__ import annotations

from difflib import SequenceMatcher


def is_near_duplicate(text: str, previous: list[str], threshold: float = 0.72) -> bool:
    needle = _norm(text)
    if not needle:
        return False
    for old in previous:
        if SequenceMatcher(None, needle, _norm(old)).ratio() >= threshold:
            return True
    return False


def _norm(text: str) -> str:
    return " ".join(text.lower().split())
