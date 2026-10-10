"""
Scoring for lead selection: which phone to dial, and how to rank the lead.

Scores a lead's phones (mobile/direct bonus, bad-status exclusion), checks
status and balance gates, and returns a dialer-ready record or None.
"""

from __future__ import annotations

from .timezone import is_dialable, utc_offset

WORKABLE_STATUSES = {"active", "new", "skip2", "skip3"}
EXCLUDED_PHONE_STATUSES = {"bad", "dnc", "disconnected", "fax"}
MIN_BALANCE = 100.0


def score_phone(phone_type: str | None, phone_status: str | None) -> int:
    if phone_status in EXCLUDED_PHONE_STATUSES:
        return -1
    score = 0
    if phone_type == "mobile":
        score += 20
    elif phone_type == "landline":
        score += 5
    if phone_type in ("direct", "mobile"):
        score += 10
    return score


def _rank_from_score(score: int) -> int:
    if score >= 25:
        return 99
    if score >= 10:
        return 50
    return 25


def select_lead(lead: dict) -> dict | None:
    if lead.get("status") not in WORKABLE_STATUSES:
        return None

    state = lead.get("state", "")
    if not state or not is_dialable(state):
        return None

    try:
        balance = float(lead.get("balance", 0))
    except (TypeError, ValueError):
        balance = 0
    if balance < MIN_BALANCE:
        return None

    phones = lead.get("phones", [])
    usable = [
        (p, score_phone(p.get("type"), p.get("status")))
        for p in phones
        if score_phone(p.get("type"), p.get("status")) >= 0
    ]
    if not usable:
        return None

    usable.sort(key=lambda x: x[1], reverse=True)
    primary, primary_score = usable[0]

    return {
        "entry_list_id": lead.get("id"),
        "phone_number": primary.get("number"),
        "rank": _rank_from_score(primary_score),
        "timezone_offset": utc_offset(state),
        "comments": f"{balance} | {lead.get('creditor', '')}",
    }
