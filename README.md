# Hire-first ads loop (X daily, Reddit Monday, LinkedIn Thursday)

Generate-and-queue drafts so a technical founder can **get paid AI 0-1 work**, with a narrower business-partner ask. **Nothing auto-publishes.** A tick writes copy; you paste it.

Needs **Python 3** (stdlib only). How to use: [TODO.md](TODO.md). Why this shape: [docs/RESEARCH.md](docs/RESEARCH.md), [docs/ANALYSIS.md](docs/ANALYSIS.md), [docs/SPEC.md](docs/SPEC.md). Ticker internals: [docs/cursor_loop.md](docs/cursor_loop.md).

> 中文版：[README.zh.md](README.zh.md)

> **Status (2026-09-18):** offer is **paid scoped 0-1 builds first**, with the partner ask as a narrow secondary filter. `cta_url` is the GitHub Pages landing, deployed from `public/` by [.github/workflows/pages.yml](.github/workflows/pages.yml) (Pages source: **GitHub Actions**). Both landing buttons book the Cal.com fit call, and `public/og.png` is the 1200×630 link-preview card. First X post is live — the loop is steady state, no setup left.

<!-- screenshots -->
## UI

Two ways to see the queue:

```bash
python3 -m engine serve
# dashboard: http://127.0.0.1:4901    landing: http://127.0.0.1:4901/landing
```

The optional sibling `platform` wrapper (`../platform/apps/ads`, port 4901) still works. **Publishing stays manual.**

| Dashboard (queue + ledger) | Landing page |
|---|---|
| ![Dashboard](screenshots/dashboard.png) | ![Landing page](screenshots/landing.png) |
<!-- /screenshots -->

## Message

You ship AI applications 0-1 **for a fee**. You optionally want a business co-founder who already sells. Equity detail is on the landing page, not in the tweet.

## Daily loop

1. Pages is already live, so there is no per-day setup. The landing is https://williamjxj.github.io/cofounder-ads/ (local preview: `http://127.0.0.1:4901/landing`).
2. Fill or refresh today’s queue:

```bash
python3 -m engine tick
python3 -m engine status
python3 -m engine tick --date 2026-08-18
python3 -m engine --root /path/to/cofounder-ads tick
```

`tick` is **idempotent**: a second run for the same date+platform does not append another ledger row.

3. Open `queue/YYYY-MM-DD/APPROVE.md`. Copy the **Post** block from `x.md` to https://x.com/compose.
4. After it is live:

```bash
python3 -m engine published --platform x --url 'https://x.com/bestitaica/status/ID'
python3 -m engine published --platform reddit --url 'https://reddit.com/r/cofounder/comments/ID'
python3 -m engine published --platform linkedin --url 'https://www.linkedin.com/feed/update/…'
```

Log a reply:

```bash
python3 -m engine reply --platform x --from '@someone' --note 'asked about scope' --url 'https://x.com/i/status/ID'
```

Skip a queued draft without posting:

```bash
python3 -m engine skip --platform x
```

## Cadence ([calendar.yml](calendar.yml))

| Platform | Default | You do |
|---|---|---|
| X | `daily` | Approve and post |
| Reddit | `weekly`, Monday | Approve and post; read [platforms/reddit.md](platforms/reddit.md) |
| LinkedIn | `weekly`, Thursday | Approve and post; read [platforms/linkedin.md](platforms/linkedin.md) |

Daily refill (optional): `0 9 * * * /full/path/to/cofounder-ads/scripts/tick.sh`

## What the engine reads

| Input | Used for |
|---|---|
| `brief.md` `cta_url` | Appended to every draft |
| `brief.md` `x_handle` | “posting as @handle” hint in `queue/YYYY-MM-DD/x.md` |
| `calendar.yml` | Which platforms are due |
| `platforms/*.md` `max_chars` / `cadence` | Length caps; weekly weekday |
| Ledger `text` / Reddit `sub` | Near-duplicate skip, least-similar fallback, sub rotation |

X angles: `hire` / `proof` / `split` / `filter` / `partner`.

## Layout

- [brief.md](brief.md) — offer (source of truth)
- `engine/` — `tick`, `published`, `skip`, `reply`, `status`, `serve`
- `queue/YYYY-MM-DD/` — drafts + `APPROVE.md`
- `ads_ledger` / `ads_crm` (Supabase) or CSV offline
- [public/index.html](public/index.html) — landing (GitHub Pages), with Open Graph / Twitter card tags
- [public/og.png](public/og.png) — 1200×630 social card used by link previews
- [AGENTS.md](AGENTS.md) — repo instructions for coding agents (commands, gotchas)

## Verify

```bash
python3 -m unittest discover -s tests -v
```

## What this is not

Not a Buffer competitor. No Craigslist bot. No auto-login posting. No extra Python packages.
