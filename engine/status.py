from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from engine.brief import load_brief
from engine.store import (
    is_placeholder_url,
    read_rows,
    status_counts,
    unpublished_streak,
)


def collect_status(root: Path, on_date: date | None = None) -> dict[str, Any]:
    on_date = on_date or date.today()
    brief = load_brief(root / "brief.md")
    cta = str(brief.get("cta_url") or "").strip()
    ledger = root / "ledger.csv"
    counts = status_counts(ledger)
    day = on_date.isoformat()
    day_dir = root / "queue" / day
    files = sorted(p.name for p in day_dir.glob("*")) if day_dir.exists() else []
    published = sum(v for k, v in counts.items() if k.endswith(":published"))
    queued = sum(v for k, v in counts.items() if k.endswith(":queued"))
    return {
        "date": day,
        "cta_url": cta,
        "cta_ok": not is_placeholder_url(cta),
        "counts": counts,
        "queued": queued,
        "published": published,
        "x_unpublished_streak": unpublished_streak(ledger, "x"),
        "today_files": files,
        "crm_rows": len(read_rows(root / "crm.csv")),
    }


def format_status(info: dict[str, Any]) -> str:
    counts = info["counts"] or {"(empty)": 0}
    count_line = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
    files = ", ".join(info["today_files"]) or "(none)"
    cta = "ok" if info["cta_ok"] else "BLOCKED placeholder"
    return (
        f"date {info['date']}\n"
        f"cta {cta}  {info['cta_url']}\n"
        f"ledger {count_line}\n"
        f"published {info['published']}  queued {info['queued']}  "
        f"x_streak {info['x_unpublished_streak']}\n"
        f"crm {info['crm_rows']}  today {files}\n"
    )
