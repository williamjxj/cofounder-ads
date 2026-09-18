from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from engine import supabase_store
from engine.status import collect_status, format_status
from engine.tick import PLATFORMS, log_reply, mark_published, mark_skipped, run_tick


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="engine",
        description="Queue hire/partner drafts. Nothing auto-publishes.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Project root",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    tick_p = sub.add_parser("tick", help="Fill today's approve queue")
    tick_p.add_argument("--date", help="YYYY-MM-DD (default: today)")

    pub = sub.add_parser("published", help="Mark the last queued draft as posted")
    pub.add_argument("--platform", required=True, choices=PLATFORMS)
    pub.add_argument("--url", required=True)

    skip = sub.add_parser("skip", help="Mark the last queued draft as skipped")
    skip.add_argument("--platform", required=True, choices=PLATFORMS)

    reply = sub.add_parser("reply", help="Log an inbound reply")
    reply.add_argument("--platform", required=True, choices=PLATFORMS)
    reply.add_argument("--from", dest="from_handle", required=True)
    reply.add_argument("--note", default="")
    reply.add_argument("--url", default="")

    sub.add_parser("status", help="Queued vs published, CTA, streak")

    serve_p = sub.add_parser("serve", help="Local dashboard + landing (127.0.0.1)")
    serve_p.add_argument("--host", default="127.0.0.1")
    serve_p.add_argument("--port", type=int, default=4901)

    args = parser.parse_args(argv)
    root: Path = args.root.resolve()
    supabase_store.load_env_file(root / ".env")

    if args.cmd == "tick":
        on_date = date.fromisoformat(args.date) if args.date else date.today()
        result = run_tick(root, on_date=on_date)
        platforms = ", ".join(result["platforms"]) or "(none due)"
        skipped = ", ".join(result["skipped"])
        extra = f" skipped {skipped}" if skipped else ""
        print(f"Queued {platforms}{extra} -> {result['dir']}")
        if result.get("warning"):
            print(result["warning"])
        return 0
    if args.cmd == "published":
        ok = mark_published(root, args.platform, args.url)
        print("Marked published." if ok else "No queued row found for that platform.")
        return 0 if ok else 1
    if args.cmd == "skip":
        ok = mark_skipped(root, args.platform)
        print("Marked skipped." if ok else "No queued row found for that platform.")
        return 0 if ok else 1
    if args.cmd == "reply":
        log_reply(root, args.platform, args.from_handle, args.note, args.url)
        print("Logged reply (crm).")
        return 0
    if args.cmd == "status":
        print(format_status(collect_status(root)), end="")
        return 0
    if args.cmd == "serve":
        from engine.serve import serve

        serve(root, host=args.host, port=args.port)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
