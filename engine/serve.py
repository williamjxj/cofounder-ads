"""Local dashboard. Stdlib only. Binds to localhost by default."""

from __future__ import annotations

import json
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from engine.status import collect_status
from engine.store import read_rows
from engine.tick import log_reply, mark_published, mark_skipped, run_tick

STATIC_DIR = Path(__file__).resolve().parent / "static"


def serve(root: Path, host: str = "127.0.0.1", port: int = 4901) -> None:
    if host not in ("127.0.0.1", "localhost", "::1"):
        raise ValueError("engine serve only binds localhost")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: object) -> None:
            print(f"[serve] {self.address_string()} {fmt % args}")

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path
            if path in ("/", "/index.html"):
                self._file(STATIC_DIR / "dashboard.html", "text/html; charset=utf-8")
                return
            if path == "/landing":
                self._file(root / "public" / "index.html", "text/html; charset=utf-8")
                return
            if path == "/api/status":
                self._json(
                    {
                        **collect_status(root),
                        "ledger": read_rows(root / "ledger.csv")[-40:],
                        "crm": read_rows(root / "crm.csv")[-20:],
                    }
                )
                return
            if path.startswith("/queue/"):
                rel = path.lstrip("/")
                target = (root / rel).resolve()
                if not str(target).startswith(str(root.resolve())) or not target.is_file():
                    self.send_error(404)
                    return
                self._file(target, "text/markdown; charset=utf-8")
                return
            self.send_error(404)

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            body = self._read_json()
            try:
                if parsed.path == "/api/tick":
                    raw = str(body.get("date") or "").strip()
                    on_date = date.fromisoformat(raw) if raw else date.today()
                    result = run_tick(root, on_date=on_date)
                    self._json(result)
                    return
                if parsed.path == "/api/published":
                    ok = mark_published(
                        root, str(body.get("platform") or ""), str(body.get("url") or "")
                    )
                    self._json({"ok": ok})
                    return
                if parsed.path == "/api/skip":
                    ok = mark_skipped(root, str(body.get("platform") or ""))
                    self._json({"ok": ok})
                    return
                if parsed.path == "/api/reply":
                    log_reply(
                        root,
                        str(body.get("platform") or "landing"),
                        str(body.get("from_handle") or ""),
                        str(body.get("note") or ""),
                        str(body.get("url") or ""),
                    )
                    self._json({"ok": True})
                    return
            except (ValueError, RuntimeError) as exc:
                self._json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_error(404)

        def _read_json(self) -> dict:
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b"{}"
            if not raw:
                return {}
            try:
                data = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                return parse_qs(raw.decode("utf-8"))
            return data if isinstance(data, dict) else {}

        def _json(self, payload: object, code: int = 200) -> None:
            blob = json.dumps(payload, default=str).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(blob)))
            self.end_headers()
            self.wfile.write(blob)

        def _file(self, path: Path, content_type: str) -> None:
            if not path.is_file():
                self.send_error(404)
                return
            data = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"dashboard http://{host}:{port}  landing http://{host}:{port}/landing", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        httpd.server_close()
