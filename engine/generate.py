from __future__ import annotations

from datetime import date
from difflib import SequenceMatcher
from typing import Any

from engine.dedupe import is_near_duplicate

X_MAX = 280
LINKEDIN_MAX = 1300
REDDIT_SUBS = ("cofounder", "startups", "indiehackers")
ANGLES = ("hire", "proof", "split", "filter", "partner")

# Bodies leave ~50 chars for the Pages CTA.
X_BODIES: dict[str, tuple[str, ...]] = {
    "hire": (
        "I ship AI apps 0-1 on a fixed scope. You have the buyer; I land the working product. Not another engineer.",
        "Paid 0-1: messy AI problem in, usable app out, days or weeks. If you can brief it, I can ship it.",
        "Need an AI builder, not a slide deck? I take scoped work and ship. Book the landing page if you have a real brief.",
        "Solo technical founder. I build AI applications you can put in front of a customer. Fixed scope. You own the account.",
        "If you already talk to buyers and need someone who actually ships AI 0-1, that is paid work I take.",
        "Stop waiting on a mythical technical cofounder. I ship the first AI app; you keep the customer.",
    ),
    "proof": (
        "Proof I ship: career-AI pipeline (jobs, resume, interview practice) from idea to running apps. I take the next 0-1.",
        "I don't sell a catalog. I land usable AI apps. Career tooling is the proof; your brief is the next build.",
        "0-1 is the job: I have already shipped career-AI apps. Next is your scoped problem, not a six-month architecture tour.",
        "Shipped, not theorized. Career-AI stack is live. I am available for the next AI product someone will actually use.",
        "The missing piece on most AI ideas is a builder who finishes. That is the seat I sit in. Proof is already running.",
    ),
    "split": (
        "You own the customer and the close. I own scope, build, ship. AI 0-1. Paid delivery, not a committee.",
        "Role split: you bring a real brief and a buyer. I turn it into a shipped AI app. You keep the relationship.",
        "I am the 0-1 AI builder. You are the person with the account. That is the whole paid deal.",
        "I will not run your marketing. You will not write my code. You sell, I ship, we scope in writing.",
        "Clear split: delivery is mine. Pipeline is yours. If you need both done by me, we are not a fit.",
    ),
    "filter": (
        "Fit: you can brief a buyer-backed AI problem. Not a fit: ideas, no budget, or free 'trial' builds.",
        "Filter: a real user and a scoped outcome in 20 minutes. I ship 0-1. I do not collect maybe-later decks.",
        "If the work is unpaid sweat-equity for a stranger's idea, skip. If it is scoped AI delivery, talk.",
        "I say no to: no buyer, no brief, build-it-and-they-will-come. I say yes to: paid 0-1 with an owner.",
        "30-second filter: who pays, what ships, who owns the customer. If you can answer, we can talk.",
    ),
    "partner": (
        "I ship AI 0-1. If you already close work and want equity not a contractor cut, that partner conversation exists.",
        "Not hunting another builder. Hunting a business partner with deal flow. Equity after a real trial, not day-one 50%.",
        "Partner seat: you intro a qualified buyer in 30 days. I ship. Written vest after a 90-day founder trial.",
        "If you closed in the last 90 days and want to own the company with a builder who ships, read the landing page.",
        "Equity-first only if you can sell. Otherwise it is a paid build. I am clear which conversation this is.",
    ),
}

REDDIT_TITLES = (
    "Technical founder (AI, 0-1) taking scoped builds — and an optional business partner seat",
    "I ship AI apps; looking for paid briefs (and a co-founder who already sells)",
    "You sell or you have a brief. I build. Co-founder search is the long game",
)

REDDIT_BODIES: dict[str, tuple[str, ...]] = {
    "cofounder": (
        """I'm a technical founder. I ship AI applications from zero to a working product.

Primary work is paid 0-1 delivery. The partner seat is narrower: a business co-founder who already talks to buyers and will bring projects in. You own the relationship and the close. I own scope, build, and shipping.

Equity-first only after a 90-day founder trial (written vest/cliff). Not a freelance split. Not a free build for a cousin's idea. 30-day filter: a qualified buyer intro, or we don't continue.

If you closed work in the last 90 days, that's the conversation.

{cta}""",
        """Co-founder search with a filter, not a wish.

I already ship AI 0-1. I do not need another engineer. I need someone who has sold in the last 90 days and wants equity instead of a contractor cut. Paid client work continues either way — the company is what we share if the trial works.

No handshake 50%. No shares that stick if nothing ships.

{cta}""",
        """What I am not: a dev shop pretending to cofound, or a builder waiting for you to invent the idea.

What I am: the 0-1 AI seat. What I want: a business co-founder with existing deal flow. Repeats of the same problem become a product we both own.

Read the landing page before DMing. If you have ideas and no buyers, this is not the thread.

{cta}""",
    ),
    "startups": (
        """Not a product launch post.

I build AI apps 0-1 (career-AI pipeline already shipped: job matching, resume, interview practice). I take scoped, paid work from people who already have a customer. I am weak at top-of-funnel sales; I am not weak at finishing.

If you have a brief and a buyer, that is a delivery conversation. If you have deal flow and want equity, that is a co-founder conversation with a 90-day trial and a 30-day intro filter.

{cta}""",
        """Technical founder for hire on AI 0-1, with an optional partner track.

I will not run your marketing while you wait. You will not be asked to code. Scope in writing. Repeats can become a product.

Wrong audience: fundraising, "passive AI income," or free trials.

{cta}""",
        """Most "we should cofound" threads die because nobody has a buyer.

I inverted it: I ship for people who already sell. If that relationship should become a company, we write vest/cliff after a trial. Until then it is paid delivery.

{cta}""",
    ),
    "indiehackers": (
        """I can ship. Selling is the bottleneck I do not pretend to have solved.

I've been landing AI applications 0-1. Career tooling is current proof, not the only thing I will build. I take paid scoped work. I am also open to a business co-founder who already has conversations with buyers.

You bring the project (paid or partner). I turn it into a shipped app.

{cta}""",
        """Building in public, asking in public.

The offer is boring on purpose: you have a real AI-shaped problem and someone who cares about the outcome. I scope, build, ship. If you are the person who keeps bringing those problems, we can talk equity.

{cta}""",
        """Indie-appropriate version: I am not launching a SaaS this week. I am filling the builder seat for AI 0-1 so the work exists in the world.

If you are sitting on a buyer conversation and no implementation, that is the fit. Link is the landing page, not a waitlist.

{cta}""",
    ),
}

LINKEDIN_BODIES = (
    """I ship AI applications from a messy brief to something a customer can use.

That is paid, scoped 0-1 work. You own the customer relationship. I own delivery. Repeats of the same problem can become a product — but the first step is a working app, not a partnership ceremony.

I am not looking for another engineer. I am not looking for an idea with no buyer. I am looking for operators who already talk to customers and need a builder who finishes.

There is a narrower partner conversation if you already close work and want equity with a written vest after a 90-day trial. Most people should start with a scoped build.

If that is you, the landing page is the next step — 20 minutes, one brief, a yes or a no.
""",
    """Role split I will actually honor:

You: pipeline, positioning, the account.
Me: scope, build, ship.

I have already landed a career-AI pipeline (job matching, resume, interview practice) from idea to running apps. That is proof of 0-1, not a catalog you must resell.

Filter: a real user and a scoped outcome. Not a fit: free custom trials, handshake 50%, or "we will figure out sales later."

Landing page in the first comment / link. I read every serious brief.
""",
    """Technical founders often wait for a business co-founder before they take money.

I flipped it. Paid AI 0-1 comes first. A partner seat exists only for people who can intro a qualified buyer in 30 days and want to own the company, not rent a contractor.

If you are hiring a builder, say so. If you are offering equity, say what you closed in the last 90 days. I will do the same on shipping.

Details and the 20-minute next step are on the landing page.
""",
)


def generate_x(
    brief: dict[str, Any],
    previous: list[str],
    on_date: date,
    max_chars: int = X_MAX,
) -> dict[str, Any]:
    cta = str(brief.get("cta_url") or "").strip()
    start = on_date.toordinal()
    candidates: list[tuple[str, str]] = []
    angle_order = _rotated(ANGLES, start)
    # Partner is secondary: push it last except Mondays.
    if on_date.weekday() != 0:
        angle_order = [a for a in angle_order if a != "partner"] + ["partner"]
    for angle in angle_order:
        bodies = X_BODIES[angle]
        body_order = _rotated(bodies, start)
        for body in body_order:
            text = _with_cta(body, cta, max_chars)
            candidates.append((angle, text))
            if not is_near_duplicate(text, previous):
                return {"angle": angle, "text": text, "chars": len(text)}
    angle, text = _least_similar(candidates, previous)
    return {"angle": angle, "text": text, "chars": len(text)}


def generate_reddit(
    brief: dict[str, Any],
    previous_subs: list[str],
    on_date: date,
    previous_texts: list[str] | None = None,
) -> dict[str, Any]:
    previous_texts = previous_texts or []
    cta = _reddit_cta(brief)
    sub = _next_sub(previous_subs)
    title = REDDIT_TITLES[on_date.toordinal() % len(REDDIT_TITLES)]
    variants = REDDIT_BODIES[sub]
    author = str(brief.get("author_name") or "").strip()
    picked = None
    candidates: list[str] = []
    for offset in range(len(variants)):
        raw = variants[(on_date.toordinal() + offset) % len(variants)]
        body = raw.format(cta=cta).strip()
        if author:
            body = f"{body}\n\n— {author}"
        candidates.append(body)
        if not is_near_duplicate(title + "\n" + body, previous_texts):
            picked = body
            break
    if picked is None:
        picked = _least_similar_text(candidates, previous_texts)
    return {"sub": sub, "title": title, "body": picked}


def generate_linkedin(
    brief: dict[str, Any],
    previous: list[str],
    on_date: date,
    max_chars: int = LINKEDIN_MAX,
) -> dict[str, Any]:
    cta = str(brief.get("cta_url") or "").strip()
    label = str(brief.get("cta_label") or "20-minute fit call").strip()
    start = on_date.toordinal()
    candidates: list[str] = []
    for offset in range(len(LINKEDIN_BODIES)):
        body = LINKEDIN_BODIES[(start + offset) % len(LINKEDIN_BODIES)].strip()
        if cta:
            body = f"{body}\n\n{label}: {cta}"
        if len(body) > max_chars:
            body = body[: max_chars - 1].rstrip() + "…"
        candidates.append(body)
        if not is_near_duplicate(body, previous):
            return {"angle": "hire", "text": body, "chars": len(body)}
    text = _least_similar_text(candidates, previous)
    return {"angle": "hire", "text": text, "chars": len(text)}


def _rotated(seq: tuple[str, ...] | list[str], start: int) -> list[str]:
    items = list(seq)
    if not items:
        return []
    k = start % len(items)
    return items[k:] + items[:k]


def _least_similar(candidates: list[tuple[str, str]], previous: list[str]) -> tuple[str, str]:
    if not candidates:
        raise ValueError("no X candidates")
    best = candidates[0]
    best_score = 2.0
    for angle, text in candidates:
        score = _max_ratio(text, previous)
        if score < best_score:
            best_score = score
            best = (angle, text)
    return best


def _least_similar_text(candidates: list[str], previous: list[str]) -> str:
    if not candidates:
        raise ValueError("no text candidates")
    best = candidates[0]
    best_score = 2.0
    for text in candidates:
        score = _max_ratio(text, previous)
        if score < best_score:
            best_score = score
            best = text
    return best


def _max_ratio(text: str, previous: list[str]) -> float:
    if not previous:
        return 0.0
    needle = " ".join(text.lower().split())
    return max(
        SequenceMatcher(None, needle, " ".join(p.lower().split())).ratio()
        for p in previous
    )


def _reddit_cta(brief: dict[str, Any]) -> str:
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
