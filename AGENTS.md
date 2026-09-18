# AGENTS.md

Hire-first ad engine: `engine/tick` writes copy drafts into `queue/YYYY-MM-DD/` for a technical founder who pastes them manually. **Nothing auto-publishes** — never add auto-post. Python 3 **stdlib only**; do not add third-party packages.

## Commands

```bash
python3 -m unittest discover -s tests -v   # tests
python3 -m engine tick                      # fill today's drafts (idempotent)
python3 -m engine tick --date YYYY-MM-DD    # backfill a specific day
python3 -m engine status                    # queued vs published, CTA, streak
python3 -m engine serve                     # dashboard :4901, landing at /landing
python3 -m engine published --platform x --url '<real url>'   # mark a posted draft
python3 -m engine skip --platform x         # drop last queued draft
python3 -m engine reply --platform x --from '@h' --note '...' # log CRM contact
```

`--root PATH` is a top-level flag: it must come **before** the subcommand (`python3 -m engine --root /path tick`).

## Layout & sources of truth

- `brief.md` — frontmatter (`cta_url`, `cta_label`, `author_name`, `x_handle`) + offer copy; source of truth for every draft. `cta_url` is appended to all drafts.
- `calendar.yml` — per-platform `cadence` (`daily` | `weekly` + `weekday` 0=Mon). X daily, Reddit Mon, LinkedIn Thu.
- `platforms/*.md` — frontmatter `max_chars`, `cadence`; doc rules for that platform. Used by the generator.
- `engine/` — `__main__.py` (CLI), `generate.py` (copy pools + near-duplicate skip), `tick.py` (due→generate→write→ledger), `store.py` (ledger/CRM read/write), `serve.py` (dashboard). See `docs/cursor_loop.md` for the wire-up.
- `public/index.html` — landing; deployed to GitHub Pages by `.github/workflows/pages.yml` (push to `master`).

## Storage

- If `.env` has `SUPABASE_URL` + `SUPABASE_SECRET_KEY`, ledger/CRM rows go to Supabase tables `ads_ledger` / `ads_crm` via REST (PostgREST), with a warning + CSV fallback on network failure.
- Otherwise rows go to the **git-tracked** `ledger.csv` / `crm.csv` — running `tick`/`reply`/`published` will dirty the working tree.
- `.env` is loaded only by the CLI entrypoint and `serve` (and the sibling `platform` wrapper). Library imports never read it, so tests always run on CSV — keep it that way.

## Gotchas

- **`queue/` is a symlink to an external drive** (`/Users/william.jiang/Samsung/cofounder-ads/queue`) and is gitignored. Drafts are never committed and live outside this repo; `tick` writes through the symlink.
- **Hand-rolled YAML subset** (`engine/yamlutil.py`): nested maps + scalars only (`yes/no`, ints, quoted/unquoted strings). No lists, no `- ` bullets, no anchors, no block scalars — a real-YAML feature will raise `ValueError` at runtime and tests will catch it.
- `tick` is idempotent: re-running the same date+platform is skipped (does not append a second ledger row).
- `published` refuses placeholder URLs (e.g. `example.com`, `you/status`) and any `cta_url` in `brief.md` that is still a placeholder.
- X bodies leave ~50 chars for the CTA; touching `brief.md` `cta_url` can silently break the 280-char cap (`generate.py:_with_cta` raises only if room < 40).
- Old seed rows once held `REPLACE_ME` CTAs, which skewed near-duplicate scoring; they now hold the real Pages URL, so dedupe works normally (again). `docs/cursor_loop.md` documents all of this.

## Tests

Suite is unit tests only (temp dirs, no network). One test is knowingly stale and fails: `test_x_markdown_includes_handle_when_set` assumes `brief.md` has an empty `x_handle`, but it now holds `"bestitaica"` — the `replace` is a no-op. Confirm 36 pass + that 1 failure before declaring a green run.