# Run requirements

What this repo needs to run, and what it does not.

| What | Needed? | Why |
|---|---|---|
| Python 3 | **Yes** | CLI and tests (`python3 -m engine`, `python3 -m unittest`) |
| pip / venv / requirements.txt | **No** | Stdlib only (argparse, csv, difflib, unittest) |
| Docker | **No** | Local files only |
| Database | **No** | `ledger.csv` and `crm.csv` |
| .env / API keys | **No** | No network publish; no LLM call |
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
| Post history | `ledger.csv` | CSV |
| Inbound replies | `crm.csv` | CSV |
| Offer copy | `brief.md` | Markdown + YAML front matter |
| Cadence | `calendar.yml` | Tiny YAML subset parsed by `engine/yamlutil.py` |

## Env and secrets

None. Do not put tokens in this repo. `cta_url` in `brief.md` is a public link, not a secret.

## What you do not need

No Docker, no Postgres, no Redis, no package install, no X/Reddit developer app, no auto-poster.
