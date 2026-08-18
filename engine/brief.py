from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.yamlutil import parse_simple_yaml


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta = parse_simple_yaml(parts[1])
    body = parts[2].lstrip("\n")
    return meta, body


def section_text(body: str, heading: str) -> str:
    marker = f"## {heading}"
    start = body.find(marker)
    if start < 0:
        return ""
    start = start + len(marker)
    nxt = body.find("\n## ", start)
    chunk = body[start:] if nxt < 0 else body[start:nxt]
    return chunk.strip()


def load_brief(path: Path) -> dict[str, Any]:
    meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
    offer = section_text(body, "Offer (one line)")
    return {
        **meta,
        "offer": offer,
        "body": body,
    }


def load_adapter(path: Path) -> dict[str, Any]:
    meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
    return {**meta, "body": body}
