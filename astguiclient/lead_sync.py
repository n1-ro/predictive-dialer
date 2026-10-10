"""
Lead sync daemon — pull scored leads from a Postgres/Supabase source into the
dialer queue, honoring per-state timezone calling windows.

This is a reference implementation with configuration placeholders. It contains
no credentials and no real lead data.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

# Per-US-state UTC offset (simplified). Real deployments use a tz database.
STATE_OFFSETS: dict[str, int] = {
    "CA": -8, "NY": -5, "TX": -6, "FL": -5, "IL": -6, "WA": -8,
}

DIALABLE_START = 9   # 9 AM local
DIALABLE_END = 21    # 9 PM local

WORKABLE_STATUSES = {"active", "new", "skip2", "skip3"}
EXCLUDED_PHONE_STATUSES = {"bad", "dnc", "disconnected", "fax"}
MIN_BALANCE = 100.0


def local_hour(state: str, now: dt.datetime | None = None) -> int:
    """Return the local hour (0–23) for a US state, given UTC now."""
    now = now or dt.datetime.now(dt.timezone.utc)
    offset = STATE_OFFSETS.get(state, -6)
    local = now + dt.timedelta(hours=offset)
    return local.hour


def is_dialable(state: str, now: dt.datetime | None = None) -> bool:
    hour = local_hour(state, now)
    return DIALABLE_START <= hour < DIALABLE_END


def score_phone(phone_type: str | None, phone_status: str | None) -> int:
    """Score a phone; returns -1 to exclude."""
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


def select_lead(lead: dict) -> dict | None:
    """Decide whether a lead should be queued, and with what rank."""
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
    scored = [
        (p, score_phone(p.get("type"), p.get("status"))) for p in phones
    ]
    usable = [(p, s) for p, s in scored if s >= 0]
    if not usable:
        return None

    usable.sort(key=lambda x: x[1], reverse=True)
    primary = usable[0][0]
    rank = 99 if usable[0][1] >= 25 else (50 if usable[0][1] >= 10 else 25)

    return {
        "entry_list_id": lead.get("id"),
        "phone_number": primary.get("number"),
        "rank": rank,
        "timezone_offset": STATE_OFFSETS.get(state, -6),
        "comments": f"{balance} | {lead.get('creditor', '')}",
    }
