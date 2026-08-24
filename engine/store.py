from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from engine import supabase_store


LEDGER_FIELDS = (
    "date",
    "platform",
    "status",
    "angle",
    "sub",
    "chars",
    "path",
    "url",
    "text",
)

CRM_FIELDS = ("date", "platform", "from_handle", "note", "url")

# Markers that indicate a URL was never replaced with a real post link.
# The engine refuses to mark a post as published while any of these appear.
PLACEHOLDER_URL_MARKERS = (
    "replace_me",
    "example.com",
    "you/status",
    "your-status-url",
    "your_post_url",
)


def is_placeholder_url(url: str) -> bool:
    low = (url or "").lower()
    return not low or any(marker in low for marker in PLACEHOLDER_URL_MARKERS)


def ensure_csv(path: Path, fields: tuple[str, ...]) -> None:
    if supabase_store.enabled():
        return
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        csv.DictWriter(fh, fieldnames=fields).writeheader()


def append_row(path: Path, fields: tuple[str, ...], row: dict[str, str]) -> None:
    if supabase_store.enabled():
        supabase_store.insert_row(path, {k: row.get(k, "") for k in fields})
        return
    ensure_csv(path, fields)
    with path.open("a", encoding="utf-8", newline="") as fh:
        csv.DictWriter(fh, fieldnames=fields).writerow(
            {k: row.get(k, "") for k in fields}
        )


def read_rows(path: Path) -> list[dict[str, str]]:
    if supabase_store.enabled():
        return supabase_store.fetch_rows(path)
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def previous_texts(path: Path, platform: str) -> list[str]:
    return [
        row["text"]
        for row in read_rows(path)
        if row.get("platform") == platform and row.get("text")
    ]


def previous_subs(path: Path) -> list[str]:
    return [
        row["sub"]
        for row in read_rows(path)
        if row.get("platform") == "reddit" and row.get("sub")
    ]


def update_last_status(
    path: Path,
    platform: str,
    status: str,
    url: str = "",
) -> bool:
    if supabase_store.enabled():
        row_id = supabase_store.find_last_queued(path, platform)
        if row_id is None:
            return False
        fields = {"status": status}
        if url:
            fields["url"] = url
        supabase_store.update_row(path, row_id, fields)
        return True
    rows = read_rows(path)
    for row in reversed(rows):
        if row.get("platform") == platform and row.get("status") == "queued":
            row["status"] = status
            if url:
                row["url"] = url
            _rewrite(path, rows)
            return True
    return False


def _rewrite(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=LEDGER_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in LEDGER_FIELDS})


def write_queue_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_digest(path: Path, on_date: date, lines: list[str], warning: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = [f"# Approve — {on_date.isoformat()}", "", "Nothing auto-publishes. Copy, post, then mark published.", ""]
    body.extend(f"- {line}" for line in lines)
    if warning:
        body.extend(["", f"> {warning}"])
    path.write_text("\n".join(body) + "\n", encoding="utf-8")
