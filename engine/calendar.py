from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from engine.yamlutil import parse_simple_yaml


def load_calendar(path: Path) -> dict[str, Any]:
    return parse_simple_yaml(path.read_text(encoding="utf-8"))


def due_platforms(calendar: dict[str, Any], on_date: date) -> list[str]:
    due: list[str] = []
    platforms = calendar.get("platforms") or {}
    for name, spec in platforms.items():
        if not spec.get("enabled", True):
            continue
        cadence = spec.get("cadence", "daily")
        if cadence == "daily":
            due.append(name)
        elif cadence == "weekly":
            weekday = int(spec.get("weekday", 0))
            if on_date.weekday() == weekday:
                due.append(name)
        else:
            raise ValueError(f"Unknown cadence for {name}: {cadence}")
    return due
