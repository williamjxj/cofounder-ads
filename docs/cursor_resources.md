# Run requirements

What this repo needs to run, and what it does not.

| What | Needed? | Why |
|---|---|---|
| Python 3 | **Yes** | CLI and tests (`python3 -m engine`, `python3 -m unittest`) |
| pip / venv / requirements.txt | **No** | Stdlib only (argparse, csv, difflib, urllib, unittest) |
| Docker | **No** | Local files only |
| Database | **Optional** | Supabase REST (`ads_ledger` / `ads_crm`); CSV fallback (`ledger.csv` / `crm.csv`) |
| .env / API keys | **Optional** | `SUPABASE_URL` + `SUPABASE_SECRET_KEY` when using Supabase storage; otherwise none |
| X or Reddit API | **No** | You paste drafts by hand |
| Node.js | **No** | Landing page is static HTML |
| Cloud hosting | **Optional** | Only if you put `public/index.html` on the web and set `cta_url` |

## Commands

```bash
python3 -m engine tick
python3 -m unittest discover -s tests -v
```

Optional daily queue fill: `scripts/tick.sh` (see README crontab example).

## Storage

| What | Where | Type |
|---|---|---|
| Queued drafts | `queue/YYYY-MM-DD/` | Markdown |
| Post history | Supabase `ads_ledger` (or `ledger.csv` offline) | PostgREST / CSV |
| Inbound replies | Supabase `ads_crm` (or `crm.csv` offline) | PostgREST / CSV |
| Offer copy | `brief.md` | Markdown + YAML front matter |
| Cadence | `calendar.yml` | Tiny YAML subset parsed by `engine/yamlutil.py` |

## Env and secrets

Optional: `SUPABASE_URL` + `SUPABASE_SECRET_KEY` in `.env` (gitignored) switch
the ledger/CRM storage to Supabase. `cta_url` in `brief.md` is a public link,
not a secret. The CLI loads `.env` automatically; tests never load it.

## What you do not need

No Docker, no self-hosted database (Supabase is optional — CSV works),
no Redis, no package install, no X/Reddit developer app, no auto-poster.
