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

   `python3 -m engine published --platform x --url https://x.com/bestitaica/status/ID`

## Rules

- Stay at or under 280 characters unless you have Premium long-form and raise `max_chars`.
- One post, one CTA (the landing page).
- Do not lead with “business opportunity” or fundraising.
- Default angles are hire / proof / split / filter. Partner is secondary (more likely on Mondays).
- The tick prefers a non-duplicate body; if the pool is spent it takes the **least similar** candidate, not body 0.
- Hashtags: at most one. Tag people only if you actually know them.
- Check the link preview before posting. X caches cards per exact URL, so a URL that was already posted can keep showing an old card; adding a query string (e.g. `?v=2`) forces a fresh scrape. Same trap if the landing's `og:` tags changed.

## Cadence

Daily draft. Skip a day if a real conversation is in progress — `skip` rather than stacking unanswered asks.

## Voice

First person, specific, short. Builder for hire first; partner ask second.
