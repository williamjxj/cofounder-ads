# Research (2026-09-17)

Sources: this repo, GitHub `williamjxj/cofounder-ads`, last-30-day founder/SaaS discussions, and public pages for founder social tools and solo AI builders.

## What this repo actually is

A **human-in-the-loop draft queue** for X (daily) and Reddit (weekly). Python 3 stdlib. Nothing posts. A landing page exists but the CTA was `REPLACE_ME`. By 2026-09-15 the engine had queued ~31 drafts and **published zero**. Copy was a 12-body loop. The sibling `platform` dashboard is local-only and not required to run the CLI.

The original offer was: technical founder seeks an unpaid business co-founder who brings deals.

## Cofounder-search as a money strategy

YC Co-Founder Matching anecdotes (r/ycombinator, r/founder, r/startups, 2025–2026): success exists, but the hit rate is brutal — on the order of **1 real partner per 40–200 conversations**, often over **months to years**. Noise is high: idea people, agencies posing as founders, ghosting. X only works if you already have presence. Handing all GTM to a sweat-equity “growth cofounder” **before revenue** is a known trap (r/cofoundermatch, Sep 2026): agency urgency kills SaaS compounding, and founder-voice distribution cannot be fully outsourced.

**Verdict:** cofounder-search-only is not a near-term way to get paid.

## Selling *this repo* as a SaaS

Founder social tools already occupy the slot: Kleo (~$49/mo, approve-then-schedule, site crawl, voice rules), FounderDistro (product URL → week of LinkedIn/X, human approve, $0–$29), PostAI / Kickpost / Made4Founders ($9–$49, multi-platform, AI writer). ChatGPT already writes cofounder tweets.

This engine’s 12 canned lines, no scheduler, no voice model, no analytics, 1 GitHub star — **not a defensible product**. Do not compete there.

## What *does* convert for solo AI builders (2026)

Pattern from solo AI / technical-partner sites (fixed-scope 0-1, book a short call, proof of shipped work, you-sell / I-build split):

| Trait | Why it converts |
|---|---|
| Paid offer first | Cash in weeks, not a year of matching |
| Proof, not a catalog | One shipped pipeline beats a portfolio dump |
| Human approve before post | Avoids ban + “sounds like a bot” |
| Landing with one CTA | Tweets without a URL die |
| CRM of inbound | Replies are the asset |
| Platform-native copy | X ≠ Reddit ≠ LinkedIn |
| Idempotent cadence | Dead queues hide that you never posted |
| Partner as filter, not the business | Equity only after they can intro a buyer |

## What we steal (and what we refuse)

Steal: dual funnel (hire + partner), GitHub Pages as the public CTA, LinkedIn long-form, in-repo dashboard so the loop is one command, publish/skip/reply from the UI, stale-queue warnings, a much larger copy pool with least-similar fallback.

Refuse: auto-login posting, Craigslist-style blasts, extra Python packages, building another Buffer.
