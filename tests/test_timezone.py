import pytest

from astguiclient.timezone import is_dialable, local_hour, next_dialable, utc_offset, is_dst

import datetime as dt


def test_local_hour_applies_offset():
    # 15:00 UTC = 7 AM in CA (-8) → not dialable
    now = dt.datetime(2026, 1, 5, 15, 0, tzinfo=dt.timezone.utc)
    assert local_hour("CA", now) == 7


def test_is_dst_detects_summer():
    summer = dt.datetime(2026, 7, 1, 12, 0, tzinfo=dt.timezone.utc)
    winter = dt.datetime(2026, 1, 1, 12, 0, tzinfo=dt.timezone.utc)
    assert is_dst(summer) is True
    assert is_dst(winter) is False


def test_utc_offset_adds_dst_hour():
    summer = dt.datetime(2026, 7, 1, 12, 0, tzinfo=dt.timezone.utc)
    assert utc_offset("CA", summer) == -7  # -8 + 1 DST


def test_is_dialable_respects_window():
    assert is_dialable("NY", dt.datetime(2026, 1, 5, 14, 0, tzinfo=dt.timezone.utc)) is True
    assert is_dialable("NY", dt.datetime(2026, 1, 5, 5, 0, tzinfo=dt.timezone.utc)) is False


def test_next_dialable_advances_forward():
    midnight = dt.datetime(2026, 1, 5, 5, 0, tzinfo=dt.timezone.utc)  # not dialable in NY
    nxt = next_dialable("NY", midnight)
    assert nxt > midnight
    assert is_dialable("NY", nxt) is True
