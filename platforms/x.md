---
id: x
enabled_by_default: true
max_chars: 280
cadence: daily
language: en
---

# X (Twitter)

## How to post

1. Open today’s `queue/YYYY-MM-DD/x.md`.
2. Copy the `Post` block only (not the notes).
3. Paste into https://x.com/compose.
4. After it is live, run:

   `python3 -m engine published --platform x --url https://x.com/YOUR_HANDLE/status/ID`

## Rules

- Stay at or under 280 characters unless you have Premium long-form and raise `max_chars`.
- Do not thread the partner ask by default. One post, one CTA.
- Do not lead with “business opportunity” or fundraising.
- Vary the angle each day (ask / proof / split / filter). If the generator repeats a near-duplicate, the tick should refuse and retry.
- Hashtags: at most one (`#cofounder` or none). Hashtag soup reads as spam.
- Tag people only if you actually know them.

## Cadence

Daily draft. Skip a day if you already posted and got a real conversation in progress — mark the ledger `skipped` rather than stacking unanswered asks.

## Voice

First person, specific, short. Sound like a builder looking for a partner, not an ad account.
