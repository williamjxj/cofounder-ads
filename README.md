# Partner-ad loop (X first, then Reddit)

Generate-and-queue drafts for a business co-founder search. **Nothing auto-publishes.** A tick writes copy; you paste it to X (and Reddit when due).

Needs **Python 3** (stdlib only). See [docs/cursor_resources.md](docs/cursor_resources.md) for what you do not need. How the ticker works: [docs/cursor_loop.md](docs/cursor_loop.md).

## Message

You ship AI applications 0-1. You want a business co-founder who brings projects in. Equity-first; vest/cliff detail is on [public/index.html](public/index.html), not in the tweet.

## Before the first post

1. Set `cta_url` in [brief.md](brief.md) to a real page or calendar link (replace `REPLACE_ME`). Host `public/index.html` or point `cta_url` at your calendar. Until that is a real URL, ticks still run but `APPROVE.md` warns you not to publish.
2. Fill the queue (from the repo root):

```bash
python3 -m engine tick
python3 -m engine tick --date 2026-08-18
python3 -m engine tick --root /path/to/ads
```

3. Open `queue/YYYY-MM-DD/APPROVE.md`. For X, copy the **Post** block from `x.md` and paste at https://x.com/compose.
4. After it is live:

```bash
python3 -m engine published --platform x --url 'https://x.com/YOU/status/ID'
python3 -m engine published --platform reddit --url 'https://reddit.com/r/cofounder/comments/ID'
```

Log a reply:

```bash
python3 -m engine reply --platform x --from '@someone' --note 'asked about equity' --url 'https://x.com/i/status/ID'
```

Skip a queued draft without posting:

```bash
python3 -m engine skip --platform x
```

`published` and `skip` update the **last `queued` row** for that platform in `ledger.csv`. They do not post anything.

## Cadence ([calendar.yml](calendar.yml))

| Platform | Default | You do |
|---|---|---|
| X | `daily`, enabled | Approve and post |
| Reddit | `weekly`, `weekday: 0` (Monday), one sub | Approve and post; read [platforms/reddit.md](platforms/reddit.md) first |

Disable a channel with `enabled: false`. Daily refill (optional cron):

```bash
0 9 * * * /full/path/to/ads/scripts/tick.sh
```

`scripts/tick.sh` forwards extra args to `python3 -m engine tick`.

## What the engine reads

| Input | Used for |
|---|---|
| `brief.md` `cta_url` | Appended to every draft. `REPLACE_ME` triggers a digest warning. |
| `calendar.yml` | Which platforms are due that day |
| `platforms/x.md` `max_chars` | X length cap (default 280) |
| `ledger.csv` prior `text` / Reddit `sub` | Near-duplicate skip and subreddit rotation |

Front matter usage in `brief.md`:

- `cta_url` — appended to every draft. `REPLACE_ME` triggers a digest warning.
- `cta_label` — used as the markdown link text on Reddit drafts (X gets the
  raw URL, since X posts have no link text).
- `x_handle` — shown in the X publish instructions when set.
- `author_name` — documentation for you; not interpolated yet.

> **Updated 2026-08-23:** the engine now **refuses** `engine published` until
> both the post URL and `cta_url` are real (no `REPLACE_ME` / placeholder
> URLs). The fake `https://x.com/YOU/status/ID` ledger row from 2026-08-18 was
> corrected back to `queued`, and a stale duplicate queued row was removed.

X copy rotates angles `ask` / `proof` / `split` / `filter`. Reddit rotates `r/cofounder` → `r/startups` → `r/indiehackers`.

## Layout

- [brief.md](brief.md) - offer, proof, angles (source of truth for the *message*)
- [platforms/x.md](platforms/x.md), [platforms/reddit.md](platforms/reddit.md), [platforms/_template.md](platforms/_template.md)
- `engine/` - `tick`, `published`, `skip`, `reply`
- [calendar.yml](calendar.yml)
- `queue/YYYY-MM-DD/` - `x.md`, `reddit.md` (Mondays), `APPROVE.md`
- `ledger.csv` - date, platform, status, angle, sub, chars, path, url, text
- `crm.csv` - date, platform, from_handle, note, url
- [public/index.html](public/index.html) - landing; [public/index.md](public/index.md) is the same copy in markdown

## Verify

```bash
python3 -m unittest discover -s tests -v
```

## What this is not

No Craigslist bot. No identical paste across platforms. No auto-login posting. No extra Python packages.
