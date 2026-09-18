from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Callable

from engine.brief import load_adapter, load_brief
from engine.calendar import due_platforms, load_calendar
from engine.generate import generate_linkedin, generate_reddit, generate_x
from engine.store import (
    CRM_FIELDS,
    LEDGER_FIELDS,
    append_row,
    ensure_csv,
    has_row_for,
    is_placeholder_url,
    previous_subs,
    previous_texts,
    unpublished_streak,
    update_last_status,
    write_digest,
    write_queue_file,
)

PLATFORMS = ("x", "reddit", "linkedin")
STALE_AFTER = 5


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
    skipped: list[str] = []

    for platform in due:
        if has_row_for(ledger_path, on_date, platform):
            skipped.append(platform)
            digest_lines.append(
                f"[ ] {platform} — already queued for {on_date.isoformat()} (idempotent skip)"
            )
            continue
        adapter = load_adapter(root / "platforms" / f"{platform}.md")
        handler = _HANDLERS.get(platform)
        if handler is None:
            raise ValueError(f"No generator for platform: {platform}")
        line = handler(root, ledger_path, brief, adapter, on_date)
        digest_lines.append(line)
        queued.append(platform)

    warning = _warnings(root, brief, ledger_path)
    write_digest(day_dir / "APPROVE.md", on_date, digest_lines, warning=warning)
    return {
        "platforms": queued,
        "skipped": skipped,
        "date": on_date.isoformat(),
        "dir": str(day_dir),
        "warning": warning,
    }


def mark_published(root: Path, platform: str, url: str) -> bool:
    _check_platform(platform)
    if is_placeholder_url(url):
        raise ValueError(
            "Refusing to mark published with a placeholder URL. "
            "Pass the real post URL (e.g. https://x.com/USER/status/ID)."
        )
    brief = load_brief(root / "brief.md")
    cta = str(brief.get("cta_url") or "").strip()
    if is_placeholder_url(cta):
        raise ValueError(
            "brief.md cta_url is not a real link yet (empty or placeholder). "
            "Set a real landing/calendar link before marking anything published."
        )
    return update_last_status(root / "ledger.csv", platform, "published", url=url)


def mark_skipped(root: Path, platform: str) -> bool:
    _check_platform(platform)
    return update_last_status(root / "ledger.csv", platform, "skipped")


def log_reply(
    root: Path,
    platform: str,
    from_handle: str,
    note: str,
    url: str = "",
) -> None:
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


def _check_platform(platform: str) -> None:
    if platform not in PLATFORMS:
        raise ValueError(f"Unknown platform: {platform}")


def _warnings(root: Path, brief: dict[str, Any], ledger_path: Path) -> str:
    parts: list[str] = []
    if is_placeholder_url(str(brief.get("cta_url") or "")):
        parts.append(
            "cta_url is still a placeholder. Do not mark posts published until it is a real link."
        )
    streak = unpublished_streak(ledger_path, "x")
    if streak >= STALE_AFTER:
        parts.append(
            f"Dead queue: {streak} X drafts are still queued with no published row after them. "
            "Paste one, or `skip` — more ticks will not get you paid."
        )
    return " ".join(parts)


def _queue_x(
    root: Path,
    ledger_path: Path,
    brief: dict[str, Any],
    adapter: dict[str, Any],
    on_date: date,
) -> str:
    post = generate_x(
        brief,
        previous=previous_texts(ledger_path, "x"),
        on_date=on_date,
        max_chars=int(adapter.get("max_chars") or 280),
    )
    rel = Path("queue") / on_date.isoformat() / "x.md"
    x_handle = str(brief.get("x_handle") or "").strip()
    write_queue_file(root / rel, _x_markdown(on_date, post, x_handle))
    _append_ledger(ledger_path, on_date, "x", post["angle"], "", post["chars"], rel, post["text"])
    return f"[ ] x — `{rel}` — {post['chars']} chars — angle {post['angle']}"


def _queue_reddit(
    root: Path,
    ledger_path: Path,
    brief: dict[str, Any],
    adapter: dict[str, Any],
    on_date: date,
) -> str:
    del adapter
    post = generate_reddit(
        brief,
        previous_subs=previous_subs(ledger_path),
        on_date=on_date,
        previous_texts=previous_texts(ledger_path, "reddit"),
    )
    rel = Path("queue") / on_date.isoformat() / "reddit.md"
    write_queue_file(root / rel, _reddit_markdown(on_date, post))
    text = post["title"] + "\n" + post["body"]
    _append_ledger(ledger_path, on_date, "reddit", "", post["sub"], len(post["body"]), rel, text)
    return f"[ ] reddit — `{rel}` — r/{post['sub']}"


def _queue_linkedin(
    root: Path,
    ledger_path: Path,
    brief: dict[str, Any],
    adapter: dict[str, Any],
    on_date: date,
) -> str:
    post = generate_linkedin(
        brief,
        previous=previous_texts(ledger_path, "linkedin"),
        on_date=on_date,
        max_chars=int(adapter.get("max_chars") or 1300),
    )
    rel = Path("queue") / on_date.isoformat() / "linkedin.md"
    write_queue_file(root / rel, _linkedin_markdown(on_date, post))
    _append_ledger(
        ledger_path, on_date, "linkedin", post["angle"], "", post["chars"], rel, post["text"]
    )
    return f"[ ] linkedin — `{rel}` — {post['chars']} chars"


def _append_ledger(
    ledger_path: Path,
    on_date: date,
    platform: str,
    angle: str,
    sub: str,
    chars: int,
    rel: Path,
    text: str,
) -> None:
    append_row(
        ledger_path,
        LEDGER_FIELDS,
        {
            "date": on_date.isoformat(),
            "platform": platform,
            "status": "queued",
            "angle": angle,
            "sub": sub,
            "chars": str(chars),
            "path": str(rel),
            "url": "",
            "text": text,
        },
    )


def _x_markdown(on_date: date, post: dict[str, Any], x_handle: str = "") -> str:
    handle_hint = f" (posting as @{x_handle})" if x_handle else ""
    return (
        f"# X draft — {on_date.isoformat()}\n\n"
        f"Angle: {post['angle']}\n"
        f"Chars: {post['chars']} / 280\n\n"
        f"## Post\n\n"
        f"{post['text']}\n\n"
        f"## How to publish\n\n"
        f"1. Copy the Post block above.\n"
        f"2. Paste at https://x.com/compose{handle_hint}\n"
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


def _linkedin_markdown(on_date: date, post: dict[str, Any]) -> str:
    return (
        f"# LinkedIn draft — {on_date.isoformat()}\n\n"
        f"Angle: {post['angle']}\n"
        f"Chars: {post['chars']}\n\n"
        f"## Post\n\n"
        f"{post['text']}\n\n"
        f"## How to publish\n\n"
        f"1. Copy the Post block.\n"
        f"2. Paste at https://www.linkedin.com/feed/\n"
        f"3. Then: `python3 -m engine published --platform linkedin --url YOUR_POST_URL`\n"
    )


_HANDLERS: dict[str, Callable[..., str]] = {
    "x": _queue_x,
    "reddit": _queue_reddit,
    "linkedin": _queue_linkedin,
}
