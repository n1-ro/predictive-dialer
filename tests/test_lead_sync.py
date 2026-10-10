import pytest

from astguiclient.lead_sync import (
    is_dialable,
    local_hour,
    score_phone,
    select_lead,
)

import datetime as dt


def test_local_hour_applies_offset():
    # 15:00 UTC = 7 AM in CA (-8) → not dialable
    now = dt.datetime(2026, 1, 5, 15, 0, tzinfo=dt.timezone.utc)
    assert local_hour("CA", now) == 7


def test_is_dialable_respects_window():
    assert is_dialable("NY", dt.datetime(2026, 1, 5, 14, 0, tzinfo=dt.timezone.utc)) is True   # 9 AM
    assert is_dialable("NY", dt.datetime(2026, 1, 5, 5, 0, tzinfo=dt.timezone.utc)) is False   # midnight


def test_score_phone_excludes_bad_statuses():
    assert score_phone("mobile", "dnc") == -1
    assert score_phone("mobile", None) > score_phone("landline", None)


def test_select_lead_requires_dialable_and_balance():
    base = {"id": "1", "status": "active", "state": "NY", "balance": 200, "phones": []}
    # No phones
    assert select_lead(base) is None

    with_phone = {**base, "phones": [{"type": "mobile", "status": None, "number": "2125550100"}]}
    out = select_lead(with_phone)
    assert out is not None
    assert out["phone_number"] == "2125550100"


def test_select_lead_rejects_below_min_balance():
    lead = {"id": "1", "status": "active", "state": "NY", "balance": 50,
            "phones": [{"type": "mobile", "status": None, "number": "2125550100"}]}
    assert select_lead(lead) is None
