from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from engine.brief import load_adapter, load_brief
from engine.calendar import due_platforms, load_calendar
from engine.generate import generate_reddit, generate_x
from engine.store import (
    CRM_FIELDS,
    LEDGER_FIELDS,
    append_row,
    ensure_csv,
    previous_subs,
    previous_texts,
    update_last_status,
    write_digest,
    write_queue_file,
)


def run_tick(root: Path, on_date: date | None = None) -> dict[str, Any]:
    on_date = on_date or date.today()
    brief = load_brief(root / "brief.md")
    calendar = load_calendar(root / "calendar.yml")
    due = due_platforms(calendar, on_date)
    ledger_path = root / "ledger.csv"
    ensure_csv(ledger_path, LEDGER_FIELDS)
    ensure_csv(root / "crm.csv", CRM_FIELDS)

    day_dir = root / "queue" / on_date.isoformat()
    digest_lines: list[str] = []
    queued: list[str] = []

    for platform in due:
        adapter = load_adapter(root / "platforms" / f"{platform}.md")
        if platform == "x":
            post = generate_x(
                brief,
                previous=previous_texts(ledger_path, "x"),
                on_date=on_date,
                max_chars=int(adapter.get("max_chars") or 280),
            )
            rel = Path("queue") / on_date.isoformat() / "x.md"
            write_queue_file(
                root / rel,
                _x_markdown(on_date, post),
            )
            append_row(
                ledger_path,
                LEDGER_FIELDS,
                {
                    "date": on_date.isoformat(),
                    "platform": "x",
                    "status": "queued",
                    "angle": post["angle"],
                    "sub": "",
                    "chars": str(post["chars"]),
                    "path": str(rel),
                    "url": "",
                    "text": post["text"],
                },
            )
            digest_lines.append(
                f"[ ] x — `{rel}` — {post['chars']} chars — angle {post['angle']}"
            )
            queued.append("x")
        elif platform == "reddit":
            post = generate_reddit(
                brief,
                previous_subs=previous_subs(ledger_path),
                on_date=on_date,
            )
            rel = Path("queue") / on_date.isoformat() / "reddit.md"
            write_queue_file(root / rel, _reddit_markdown(on_date, post))
            append_row(
                ledger_path,
                LEDGER_FIELDS,
                {
                    "date": on_date.isoformat(),
                    "platform": "reddit",
                    "status": "queued",
                    "angle": "",
                    "sub": post["sub"],
                    "chars": str(len(post["body"])),
                    "path": str(rel),
                    "url": "",
                    "text": post["title"] + "\n" + post["body"],
                },
            )
            digest_lines.append(
                f"[ ] reddit — `{rel}` — r/{post['sub']}"
            )
            queued.append("reddit")
        else:
            raise ValueError(f"No generator for platform: {platform}")

    warning = ""
    if str(brief.get("cta_url") or "") in ("", "REPLACE_ME"):
        warning = "cta_url is still REPLACE_ME. Do not mark posts published until it is a real link."

    write_digest(day_dir / "APPROVE.md", on_date, digest_lines, warning=warning)
    return {"platforms": queued, "date": on_date.isoformat(), "dir": str(day_dir)}


def mark_published(root: Path, platform: str, url: str) -> bool:
    return update_last_status(root / "ledger.csv", platform, "published", url=url)


def mark_skipped(root: Path, platform: str) -> bool:
    return update_last_status(root / "ledger.csv", platform, "skipped")


def log_reply(root: Path, platform: str, from_handle: str, note: str, url: str = "") -> None:
    ensure_csv(root / "crm.csv", CRM_FIELDS)
    append_row(
        root / "crm.csv",
        CRM_FIELDS,
        {
            "date": date.today().isoformat(),
            "platform": platform,
            "from_handle": from_handle,
            "note": note,
            "url": url,
        },
    )


def _x_markdown(on_date: date, post: dict[str, Any]) -> str:
    return (
        f"# X draft — {on_date.isoformat()}\n\n"
        f"Angle: {post['angle']}\n"
        f"Chars: {post['chars']} / 280\n\n"
        f"## Post\n\n"
        f"{post['text']}\n\n"
        f"## How to publish\n\n"
        f"1. Copy the Post block above.\n"
        f"2. Paste at https://x.com/compose\n"
        f"3. Then: `python3 -m engine published --platform x --url YOUR_STATUS_URL`\n"
    )


def _reddit_markdown(on_date: date, post: dict[str, Any]) -> str:
    return (
        f"# Reddit draft — {on_date.isoformat()}\n\n"
        f"Subreddit: r/{post['sub']}\n"
        f"Read `platforms/reddit.md` before submitting.\n\n"
        f"## Title\n\n"
        f"{post['title']}\n\n"
        f"## Body\n\n"
        f"{post['body']}\n\n"
        f"## How to publish\n\n"
        f"1. Open https://www.reddit.com/r/{post['sub']}/submit\n"
        f"2. Paste title and body.\n"
        f"3. Then: `python3 -m engine published --platform reddit --url YOUR_POST_URL`\n"
    )
