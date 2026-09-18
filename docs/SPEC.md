# Spec

## Product

A local **GTM loop** for one operator: generate platform-native drafts, approve, paste, mark published, log replies. Public surface is a static landing page.

Nothing auto-publishes to X, Reddit, or LinkedIn.

## Offers (from `brief.md`)

1. **Hire (default):** fixed-scope AI 0-1. They own the customer; you ship.
2. **Partner (filter):** equity after a 90-day trial; 30-day buyer-intro gate.

Every draft appends `cta_url` — the Pages landing at https://williamjxj.github.io/cofounder-ads/, deployed from `public/` by `.github/workflows/pages.yml` (Pages source: GitHub Actions). Both landing buttons now book the Cal.com fit call (`cal.com/bestitconsultingca/fit-call`); the `hire` / `partner` GitHub issue templates stay in `.github/ISSUE_TEMPLATE/` but the landing no longer links them.

The landing carries hand-written Open Graph / Twitter card tags and a 1200×630 `public/og.png`, so a pasted link renders a title, description, and thumbnail instead of a bare URL.

## CLI (stdlib)

| Command | Effect |
|---|---|
| `python3 -m engine tick [--date]` | Queue due platforms. **Idempotent** per date+platform. |
| `python3 -m engine published --platform x\|reddit\|linkedin --url URL` | Last queued → published (real URLs only). |
| `python3 -m engine skip --platform …` | Last queued → skipped. |
| `python3 -m engine reply …` | Append CRM. |
| `python3 -m engine status` | Counts, unpublished streak, CTA check, today’s files. |
| `python3 -m engine serve [--port]` | `127.0.0.1` dashboard + `/landing`. |

## Calendar

| Platform | Cadence |
|---|---|
| x | daily |
| reddit | weekly Monday |
| linkedin | weekly Thursday |

## Generator

- X: angles `hire` / `proof` / `split` / `filter` / `partner`. ≥5 bodies each. Prefer non-duplicate; else **least-similar**, never silently recycle body 0.
- Reddit: rotate subs; **multiple bodies per sub**; skip near-duplicates vs ledger `text`.
- LinkedIn: long-form hire-primary, ≤ 1300 chars by default.
- Do not say: investment, fundraising, passive income, “business opportunity.”

## Storage

Unchanged: Supabase `ads_ledger` / `ads_crm` when env is set, else CSV. Network errors on Supabase raise a clear `RuntimeError` (no traceback-only `URLError`). Ledger schema unchanged (`angle` holds hire/proof/…).

## Dashboard

Read-only queue + ledger, run tick, mark published/skip, log reply. Serves `public/index.html` at `/landing`. Bind localhost.

## Out of scope

OAuth posting, extra pip deps, pricing on the tweet, multi-tenant SaaS.
