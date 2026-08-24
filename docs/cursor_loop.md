# How the ticker works

Maps to the code in `engine/`. Nothing in this loop publishes to X or Reddit.

```text
brief.md + calendar.yml + platforms/*.md + Supabase ads_ledger (or ledger.csv offline)
        -> python3 -m engine tick [--date YYYY-MM-DD] [--root PATH]
        -> queue/YYYY-MM-DD/{x.md,reddit.md,APPROVE.md}
        -> new ads_ledger rows with status=queued (or CSV rows offline)
        -> you paste, then `published` or `skip`
        -> inbound notes go to ads_crm via `reply` (or crm.csv offline)
```

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

## Tick behavior

1. Load `brief.md` and `calendar.yml`.
2. Ensure `ads_ledger` / `ads_crm` exist in Supabase (see `migrations/supabase.sql`),
   or `ledger.csv` / `crm.csv` headers exist when not configured.
3. For each due platform, load `platforms/<id>.md`.
4. **X:** pick an angle by date, skip near-duplicates, append `cta_url`, write `queue/<date>/x.md`.
5. **Reddit:** next sub after the last ledger `sub`, write `reddit.md` (title + body).
6. Write `APPROVE.md`. If `cta_url` is missing or `REPLACE_ME`, add a do-not-publish warning.

Unknown platform ids in `calendar.yml` raise. Adding LinkedIn later is a new adapter file plus a generator branch, not a scrape.

## Tests

`tests/test_calendar.py`, `test_dedupe.py`, `test_generate.py`, `test_store.py`,
`test_supabase_store.py` cover due days, dedupe, X/Reddit generation, tick
outputs, `published`, `reply`, and the Supabase storage layer (offline).
