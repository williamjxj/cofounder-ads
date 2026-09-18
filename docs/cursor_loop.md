# How the ticker works

Maps to the code in `engine/`. Nothing in this loop publishes to X, Reddit, or LinkedIn.

```text
brief.md + calendar.yml + platforms/*.md + ledger
        -> python3 -m engine [--root PATH] tick [--date YYYY-MM-DD]
        -> queue/YYYY-MM-DD/{x.md,reddit.md,linkedin.md,APPROVE.md}
        -> ledger row status=queued (skipped if that date+platform already exists)
        -> python3 -m engine serve  (or the sibling platform dashboard)
        -> you paste, then published / skip / reply
        -> python3 -m engine status  (weekly evaluate)
```

`--root` is a top-level flag: it must come *before* the subcommand.

## Modules

| File | Role |
|---|---|
| `engine/__main__.py` | CLI: `tick`, `published`, `skip`, `reply`, `status`, `serve` |
| `engine/tick.py` | Due platforms → generate → queue files → ledger append; idempotent |
| `engine/brief.py` | Loads `brief.md` front matter and `platforms/*.md` adapters |
| `engine/yamlutil.py` | Tiny YAML subset parser (nested maps + scalars only) |
| `engine/calendar.py` | `daily` every day; `weekly` on `weekday` (0=Monday) |
| `engine/generate.py` | X / Reddit / LinkedIn; least-similar fallback |
| `engine/dedupe.py` | Near-duplicate scorer behind the least-similar pick |
| `engine/store.py` | Ledger/CRM rows, placeholder-URL guard, digests, queue files |
| `engine/supabase_store.py` | PostgREST storage for `ads_ledger` / `ads_crm`; CSV fallback |
| `engine/status.py` | Counts, CTA check, unpublished streak |
| `engine/serve.py` | Localhost dashboard |
| `engine/static/dashboard.html` | Dashboard UI served by `serve.py` |
| `public/index.html` | Landing (GitHub Pages artifact) + og/twitter card tags |
| `public/og.png` | 1200×630 social card used by link previews |

## Tick behavior

1. Load `brief.md` and `calendar.yml`.
2. Ensure ledger/CRM exist.
3. For each due platform, skip if a row for that date+platform already exists.
4. Else generate, write queue file, append `queued`.
5. Write `APPROVE.md`. Warn on placeholder CTA or a long unpublished X streak.

## Known gaps (closed 2026-09-17 vs 2026-09-15)

| Was | Now |
|---|---|
| 12-body X pool recycled body 0 | Larger pool + least-similar fallback |
| One Reddit body per sub | Three variants per sub + dedupe |
| Tick not idempotent | Skip if date+platform exists |
| Dead queue invisible | Streak warning + `engine status` |
| `URLError` traceback | `RuntimeError` with a clear message |
| Dashboard only in sibling repo | `python3 -m engine serve` |
| CTA placeholder token | Real GitHub Pages URL |

Still operator-owned: paste drafts manually (auto-post stays off) and eyeball the X link-preview card before posting — X caches cards per exact URL, so an already-posted URL can keep an old preview. `cta_url` stays on the landing; booking happens through the Cal.com buttons on the page. Supabase outages fall back to CSV with a stderr warning.

## Tests

`tests/` covers cadence, dedupe, X/Reddit/LinkedIn generation, idempotent tick, publish guards, status CTA, Supabase env, and URLError wrapping.
