# How the ticker works

Maps to the code in `engine/`. Nothing in this loop publishes to X or Reddit.

```text
brief.md + calendar.yml + platforms/*.md + Supabase ads_ledger (or ledger.csv offline)
        -> python3 -m engine [--root PATH] tick [--date YYYY-MM-DD]
        -> queue/YYYY-MM-DD/{x.md,reddit.md,APPROVE.md}
        -> new ads_ledger rows with status=queued (or CSV rows offline)
        -> ../platform/apps/ads/server.mjs (dashboard, :4901) reads the queue + ledger
        -> you paste, then `published` or `skip`
        -> inbound notes go to ads_crm via `reply` (or crm.csv offline)
```

`--root` is a top-level flag: it must come *before* the subcommand
(`python3 -m engine --root PATH tick`). `tick --root PATH` is an argparse error.

## Modules

| File | Role |
|---|---|
| `engine/__main__.py` | CLI: `tick`, `published`, `skip`, `reply` |
| `engine/tick.py` | Due platforms → generate → queue files → ledger append |
| `engine/calendar.py` | `daily` every day; `weekly` on `weekday` (0=Monday) if `enabled` |
| `engine/yamlutil.py` | Nested maps, bool, int, strings (not full YAML) |
| `engine/brief.py` | YAML front matter + `##` sections |
| `engine/generate.py` | X ≤ `max_chars`; Reddit title/body/sub rotation |
| `engine/dedupe.py` | `SequenceMatcher` ≥ 0.72 vs prior ledger `text` |
| `engine/store.py` | CSV read/write; Supabase REST when `SUPABASE_URL` + `SUPABASE_SECRET_KEY` set |
| `engine/supabase_store.py` | PostgREST client (stdlib urllib) for `ads_ledger` / `ads_crm` |
| `public/index.html` | Landing page (the `cta_url` target once hosted) |

The web dashboard is **not** in this repo — it lives in the sibling `platform`
project (`../platform/apps/ads/server.mjs`, app id `ads`, port 4901, bound to
`127.0.0.1`). It reads this project's `queue/` and the Supabase ledger, serves
the landing page at `/landing`, and can trigger a tick. It never publishes.

## Tick behavior

1. Load `brief.md` and `calendar.yml`.
2. Ensure `ads_ledger` / `ads_crm` exist in Supabase (see `migrations/supabase.sql`),
   or `ledger.csv` / `crm.csv` headers exist when not configured.
3. For each due platform, load `platforms/<id>.md`.
4. **X:** pick an angle by date, test candidates against prior ledger `text`
   (`engine/dedupe.py`), append `cta_url`, write `queue/<date>/x.md`. The first
   candidate that is *not* a near-duplicate wins; if the whole pool is spent the
   tick falls back to the first candidate instead of failing — see Known gaps.
5. **Reddit:** next sub after the last ledger `sub`, write `reddit.md` (title + body).
6. Write `APPROVE.md`. If `cta_url` is missing or `REPLACE_ME`, add a do-not-publish warning.

Unknown platform ids in `calendar.yml` raise. Adding LinkedIn later is a new adapter file plus a generator branch, not a scrape.

## Known gaps (verified 2026-09-15)

Checked against the live Supabase ledger and a replayed generator:

1. **The copy pool is spent.** `engine/generate.py` holds 12 X bodies (4 angles × 3)
   and 3 Reddit bodies. After ~12 daily ticks every candidate is a near-duplicate,
   so `generate_x` returns `candidates[0]` and the output cycles on a 12-day loop.
   In the live ledger, 23 drafts contain 11 unique texts. `platforms/x.md` says the
   tick "should refuse and retry" — it does not refuse.
2. **Reddit repeats verbatim.** One body per sub on a 3-sub rotation means the same
   sub gets byte-identical text every 3 weeks (`r/indiehackers` on 2026-08-24 and
   2026-09-14). `platforms/reddit.md` asks for new wording every time.
3. **`tick` is not idempotent.** Two ticks for one date append two `queued` rows and
   overwrite the queue file (reproduced in a temp copy).
4. **A dead queue is invisible.** `mark_published` refuses placeholder URLs, but
   `run_tick` has no staleness check, so it keeps queuing: 31 rows, all `queued`,
   zero `published` between 2026-08-24 and 2026-09-15.
5. **Network failure is unhandled.** `engine/supabase_store.py` wraps `HTTPError`
   but not `URLError`, so DNS/offline raises a raw traceback from the unattended
   09:00 launchd tick — no CSV fallback, no alert.
6. **`ledger.csv` is stale.** With `.env` configured all rows go to Supabase, so the
   tracked `ledger.csv` still shows only the three 2026-08-17/18 rows. Treat it as
   legacy offline storage, not as history.

## Tests

`tests/test_calendar.py`, `test_dedupe.py`, `test_generate.py`, `test_store.py`,
`test_supabase_store.py` cover due days, dedupe, X/Reddit generation, tick
outputs, `published`, `reply`, and the Supabase storage layer (offline).
