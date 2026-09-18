---
id: linkedin
enabled_by_default: true
max_chars: 1300
cadence: weekly
weekday: 3
language: en
---

# LinkedIn

Weekly long-form. Hire-primary. Do not paste the X draft.

## How to post

1. Open `queue/YYYY-MM-DD/linkedin.md`.
2. Copy the Post block into https://www.linkedin.com/feed/
3. After it is live:

   `python3 -m engine published --platform linkedin --url YOUR_POST_URL`

## Rules

- Native LinkedIn voice: role split, proof, filter. No hashtag soup.
- One post per due Thursday.
- Comment on your own post with the landing URL if the composer eats the link.
