from __future__ import annotations

from datetime import date
from typing import Any

from engine.dedupe import is_near_duplicate

X_MAX = 280
REDDIT_SUBS = ("cofounder", "startups", "indiehackers")
ANGLES = ("ask", "proof", "split", "filter")

# Bodies are written to leave room for a CTA URL (budget ~80 chars).
X_BODIES: dict[str, tuple[str, ...]] = {
    "ask": (
        "I ship AI apps 0-1. Looking for a business co-founder who already talks to buyers. You bring projects, I build. Equity, not freelance.",
        "Technical founder here. I land AI products 0-1. Need a business co-founder with real deal flow, not another builder.",
        "Seeking a business co-founder: you already sell, I already ship AI 0-1. Bring the projects. We share the company.",
    ),
    "proof": (
        "I already shipped a career-AI pipeline (jobs, resume, interview practice) from idea to running apps. Missing piece: a co-founder who can sell.",
        "I don't need help coding. I need a partner who closed work in the last 90 days and wants equity. I ship AI 0-1.",
        "Proof I ship: career-AI apps live from 0-1. Proof I need: a business co-founder who brings buyers, not ideas.",
    ),
    "split": (
        "You own the customer and the close. I own scope, build, ship. AI 0-1. Looking for that business co-founder.",
        "Role split: you bring projects and close. I turn them into shipped AI apps. Equity co-founder, not a contractor.",
        "I'm the 0-1 AI builder. You're the business co-founder with distribution. That's the whole deal.",
    ),
    "filter": (
        "If you closed work in the last 90 days and want to own a company with a builder who ships, let's talk. AI 0-1.",
        "Not a fit: ideas and no buyers, or free 'trial' builds. Fit: you sell, I ship, we share equity.",
        "Filter: you can intro a real buyer in 30 days. I can ship the product. Business co-founder search.",
    ),
}

REDDIT_TITLES = (
    "Technical founder (AI, 0-1) looking for a business co-founder with deal flow",
    "I ship AI apps; I need a co-founder who can bring paying projects",
    "Co-founder search: you sell, I build",
)

REDDIT_BODIES = {
    "cofounder": """I'm a technical founder. I ship AI applications from zero to a working product. What I don't have is business development or marketing.

I'm looking for a business co-founder who already talks to buyers and will bring projects in. You own the relationship and the close. I own scope, build, and shipping. Repeats become a product we both own.

Equity-first (written vest/cliff after a 90-day founder trial). Not a freelance split. Not a free build for your cousin's idea.

If you closed work in the last 90 days and want to partner with someone who can actually land 0-1, that's the conversation.

{cta}""",
    "startups": """Co-founder search, not a product launch.

I build AI apps 0-1 (I've already shipped a career-AI pipeline: job matching, resume, interview practice). I am weak at sales. I want a business co-founder with existing deal flow who will bring projects in so I can implement and productize repeats.

You sell. I ship. We share the company on a real vesting schedule after a 90-day trial. 30-day filter: a qualified buyer intro, or we don't continue.

{cta}""",
    "indiehackers": """I can ship. I cannot sell.

I've been landing AI applications 0-1 (career tooling is the current proof, not the only thing I will ever build). I'm looking for a business co-founder who already has conversations with buyers and wants equity, not a contractor cut.

If that's you: you bring the project, I turn it into a shipped app, we productize what repeats.

{cta}""",
}


def generate_x(
    brief: dict[str, Any],
    previous: list[str],
    on_date: date,
    max_chars: int = X_MAX,
) -> dict[str, Any]:
    cta = str(brief.get("cta_url") or "").strip()
    start = on_date.toordinal()
    candidates: list[tuple[str, str]] = []
    for offset in range(len(ANGLES) * 4):
        angle = ANGLES[(start + offset) % len(ANGLES)]
        bodies = X_BODIES[angle]
        body = bodies[(start + offset) % len(bodies)]
        text = _with_cta(body, cta, max_chars)
        candidates.append((angle, text))
        if not is_near_duplicate(text, previous):
            return {"angle": angle, "text": text, "chars": len(text)}
    angle, text = candidates[0]
    return {"angle": angle, "text": text, "chars": len(text)}


def generate_reddit(
    brief: dict[str, Any],
    previous_subs: list[str],
    on_date: date,
) -> dict[str, Any]:
    cta = _reddit_cta(brief)
    sub = _next_sub(previous_subs)
    title = REDDIT_TITLES[on_date.toordinal() % len(REDDIT_TITLES)]
    body = REDDIT_BODIES[sub].format(cta=cta).strip()
    return {"sub": sub, "title": title, "body": body}


def _reddit_cta(brief: dict[str, Any]) -> str:
    """Reddit supports markdown link text — use cta_label when provided."""
    cta = str(brief.get("cta_url") or "").strip()
    if not cta:
        return ""
    label = str(brief.get("cta_label") or "").strip()
    if label:
        return f"[{label}]({cta})"
    return cta


def _next_sub(previous_subs: list[str]) -> str:
    if not previous_subs:
        return REDDIT_SUBS[0]
    last = previous_subs[-1]
    if last in REDDIT_SUBS:
        return REDDIT_SUBS[(REDDIT_SUBS.index(last) + 1) % len(REDDIT_SUBS)]
    return REDDIT_SUBS[0]


def _with_cta(body: str, cta: str, max_chars: int) -> str:
    body = body.strip()
    if not cta:
        if len(body) > max_chars:
            raise ValueError(f"X draft is {len(body)} chars without a CTA")
        return body
    text = f"{body} {cta}"
    if len(text) <= max_chars:
        return text
    room = max_chars - len(cta) - 1
    if room < 40:
        raise ValueError("CTA URL is too long for an X post")
    return f"{body[: room - 1].rstrip()}… {cta}"
