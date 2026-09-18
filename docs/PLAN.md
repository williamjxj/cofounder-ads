# Plan

1. Research + analysis + spec (this folder) — done.
2. Rewrite `brief.md`, landing, issue templates, Pages workflow.
3. Generator + LinkedIn adapter + calendar.
4. Idempotent tick, staleness warning, `status`, Supabase `URLError`.
5. `engine serve` dashboard (product is self-contained).
6. Tests for new behavior; keep 27 existing cases green (updated for real CTA).
7. Verify: unittest, tick idempotency, serve `/landing`, `status` JSON-ish print.
8. Operator: enable GitHub Pages, post today’s X draft, swap calendar when ready.
9. Loop: weekly `engine status`; rewrite bodies that start repeating; promote inbound in CRM.

Execute order in this change-set is 2–7. 8–9 are production, not code.
