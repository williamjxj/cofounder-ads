# Plan

1. Research + analysis + spec (this folder) — done.
2. Rewrite `brief.md`, landing, issue templates, Pages workflow.
3. Generator + LinkedIn adapter + calendar.
4. Idempotent tick, staleness warning, `status`, Supabase `URLError`.
5. `engine serve` dashboard (product is self-contained).
6. Tests for new behavior; keep the existing cases green (37 total).
7. Verify: unittest, tick idempotency, serve `/landing`, `status` JSON-ish print.
8. Operator: Pages source → GitHub Actions ✅, landing buttons → Cal.com fit call ✅, first X post published ✅ (all done 2026-09-18).
9. Loop: weekly `engine status`; rewrite bodies that start repeating; promote inbound in CRM.

Items 2–7 are the code change-set. 8–9 are production, not code; only the weekly loop in 9 is still open.
