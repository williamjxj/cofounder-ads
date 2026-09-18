"""Supabase REST (PostgREST) storage for the ads engine.

The engine stays stdlib-only: ledger/CRM rows live in Supabase tables
(ads_ledger / ads_crm) whenever SUPABASE_URL + SUPABASE_SECRET_KEY are set,
otherwise it falls back to CSV files so the tool keeps working offline and
the test suite runs without network.

Env is loaded from the project root .env by the CLI entrypoint
(engine/__main__.py) and by the platform dashboard wrapper. Library imports
never read .env automatically, so tests and embedded usage stay on CSV.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

LEDGER_TABLE = "ads_ledger"
CRM_TABLE = "ads_crm"

TABLE_BY_FILENAME = {
    "ledger.csv": LEDGER_TABLE,
    "crm.csv": CRM_TABLE,
}

TIMEOUT_SECONDS = 15


def load_env_file(path: Path) -> None:
    """Minimal .env loader (KEY=VALUE lines, # comments). Never overrides
    variables already present in the environment."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def enabled() -> bool:
    return bool(
        os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SECRET_KEY")
    )


def table_for(path: Path) -> str:
    try:
        return TABLE_BY_FILENAME[Path(path).name]
    except KeyError:
        raise ValueError(f"No Supabase table mapped for {path!s}") from None


def _base_url() -> str:
    return os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1"


def _headers() -> dict[str, str]:
    key = os.environ["SUPABASE_SECRET_KEY"]
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Prefer": "return=minimal",
    }


def _request(method: str, url: str, payload: dict | None = None) -> bytes:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=_headers(), method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"Supabase {method} {url} failed: HTTP {exc.code} {exc.read()[:300]!r}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Supabase {method} {url} failed: network {exc.reason!r}. "
            "Unset SUPABASE_URL / SUPABASE_SECRET_KEY to use CSV, or retry when online."
        ) from exc


def fetch_rows(path: Path) -> list[dict]:
    """All rows for a table, in insertion order (id asc)."""
    url = f"{_base_url()}/{table_for(path)}?select=*&order=id.asc"
    body = _request("GET", url)
    return json.loads(body) if body else []


def insert_row(path: Path, row: dict[str, str]) -> None:
    url = f"{_base_url()}/{table_for(path)}"
    _request("POST", url, payload=row)


def update_row(path: Path, row_id: int, fields: dict[str, str]) -> None:
    url = f"{_base_url()}/{table_for(path)}?id=eq.{row_id}"
    _request("PATCH", url, payload=fields)


def find_last_queued(path: Path, platform: str) -> int | None:
    """Id of the most recent queued row for a platform (the one publish/skip
    should update), matching the CSV engine's semantics."""
    query = urllib.parse.urlencode(
        {
            "select": "id",
            "platform": f"eq.{platform}",
            "status": "eq.queued",
            "order": "id.desc",
            "limit": 1,
        }
    )
    url = f"{_base_url()}/{table_for(path)}?{query}"
    body = _request("GET", url)
    rows = json.loads(body) if body else []
    return rows[0]["id"] if rows else None
