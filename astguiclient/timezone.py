"""
Timezone-aware dialing-window helpers for the lead sync daemon.

Uses a static US-state → UTC offset map plus DST-aware adjustment for the
simplified reference implementation. Production deployments should use the
`zoneinfo` database for full accuracy.
"""

from __future__ import annotations

import datetime as dt

# Base UTC offsets (standard time). DST adds +1 during the summer window.
STATE_OFFSETS: dict[str, int] = {
    "CA": -8, "OR": -8, "WA": -8, "NV": -8,
    "AZ": -7, "CO": -7, "UT": -7,
    "TX": -6, "IL": -6, "MN": -6, "MO": -6,
    "NY": -5, "FL": -5, "GA": -5, "OH": -5, "PA": -5,
    "MA": -5, "MI": -5, "NC": -5, "VA": -5,
}

DIALABLE_START = 9
DIALABLE_END = 21


def is_dst(now: dt.datetime) -> bool:
    """Approximate US DST: second Sunday of March → first Sunday of November."""
    month = now.month
    day = now.day
    if month < 3 or month > 11:
        return False
    if month > 3 and month < 11:
        return True
    # March or November: compute the relevant Sunday boundary.
    if month == 3:
        # DST starts the second Sunday of March.
        first_sunday = 8 - ((now.replace(day=1).weekday() + 1) % 7)
        second_sunday = first_sunday + 7
        return day > second_sunday or (day == second_sunday and now.hour >= 2)
    # November: DST ends the first Sunday.
    first_sunday = 8 - ((now.replace(day=1).weekday() + 1) % 7)
    return day < first_sunday or (day == first_sunday and now.hour < 2)


def utc_offset(state: str, now: dt.datetime | None = None) -> int:
    now = now or dt.datetime.now(dt.timezone.utc)
    base = STATE_OFFSETS.get(state, -6)
    return base + (1 if is_dst(now) else 0)


def local_hour(state: str, now: dt.datetime | None = None) -> int:
    now = now or dt.datetime.now(dt.timezone.utc)
    local = now + dt.timedelta(hours=utc_offset(state, now))
    return local.hour


def is_dialable(state: str, now: dt.datetime | None = None) -> bool:
    hour = local_hour(state, now)
    return DIALABLE_START <= hour < DIALABLE_END


def next_dialable(state: str, now: dt.datetime | None = None) -> dt.datetime:
    """Return the next UTC time the state is within its dialing window."""
    now = now or dt.datetime.now(dt.timezone.utc)
    for hours in range(0, 48):
        candidate = now + dt.timedelta(hours=hours)
        if is_dialable(state, candidate):
            return candidate
    return now
