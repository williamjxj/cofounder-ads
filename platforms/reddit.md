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
2. Use the sub named in the draft.
3. Read that sub’s rules before you submit.
4. Title + body from the draft. Do not add “upvote please.”
5. After it is live:

   `python3 -m engine published --platform reddit --url https://reddit.com/r/SUB/comments/ID`

## Rotation

1. **r/cofounder** — partner-track copy. Technical 0→1 founder; paid work continues either way.
2. **r/startups** — frame as a builder taking scoped work + optional partner, not a launch. Check sidebar.
3. **r/indiehackers** — progress + ask.

Do **not** use r/entrepreneur classifieds or Craigslist-tone subs.

## Rules that apply everywhere

- One post per week from this adapter.
- Generator has multiple bodies per sub and skips near-duplicates vs the ledger.
- Engage if people comment.
- Legal/equity detail: one line + landing page.
