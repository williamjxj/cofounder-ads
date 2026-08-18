---
id: reddit
enabled_by_default: true
max_chars: 10000
cadence: weekly
weekday: 0
language: en
---

# Reddit

One sub per week. Never the same text in multiple subs on the same day.

## How to post

1. Open today’s `queue/YYYY-MM-DD/reddit.md`.
2. Use the sub named in the draft (the generator rotates).
3. Read that sub’s rules in this file before you submit.
4. Title + body from the draft. Do not add “upvote please.”
5. After it is live, run:

   `python3 -m engine published --platform reddit --url https://reddit.com/r/SUB/comments/ID`

## Rotation (pick the next sub that is due; skip if the last ledger row was this sub)

1. **r/cofounder** — people actually looking for co-founders. Best first target. Be explicit: technical 0→1 founder seeking a business co-founder with deal flow. No product spam.
2. **r/startups** — weekly is already aggressive. Self-promo rules are strict; frame as a co-founder search, not a launch. Check sidebar before posting.
3. **r/indiehackers** — progress + ask, not a classified. Lead with what you shipped, then the seat you need.

Do **not** use r/entrepreneur, r/forhire, or “opportunity” classified subs for this ask. Wrong audience, same failure mode as Craigslist.

## Rules that apply everywhere

- One post per week from this adapter.
- New wording every time. Pasting last week’s body will get removed.
- No identical cross-post. If you posted r/cofounder this week, wait for the next tick for a different sub.
- Engage if people comment. Drive-by ads get banned.
- Legal/equity detail: one line + link to the landing page. Do not paste the full vest/cliff brief into Reddit.

## Title patterns (generator picks one)

- Technical founder (AI, 0→1) looking for a business co-founder with deal flow
- I ship AI apps; I need a co-founder who can bring paying projects
- Co-founder search: you sell, I build
