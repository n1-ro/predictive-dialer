import pytest

from astguiclient.scoring import score_phone, select_lead, _rank_from_score


def test_score_phone_excludes_bad_statuses():
    assert score_phone("mobile", "dnc") == -1
    assert score_phone("mobile", None) > score_phone("landline", None)


def test_rank_from_score_buckets():
    assert _rank_from_score(30) == 99
    assert _rank_from_score(15) == 50
    assert _rank_from_score(3) == 25


def test_select_lead_requires_dialable_and_balance():
    base = {"id": "1", "status": "active", "state": "NY", "balance": 200, "phones": []}
    assert select_lead(base) is None

    with_phone = {**base, "phones": [{"type": "mobile", "status": None, "number": "2125550100"}]}
    out = select_lead(with_phone)
    assert out is not None
    assert out["phone_number"] == "2125550100"


def test_select_lead_rejects_below_min_balance():
    lead = {"id": "1", "status": "active", "state": "NY", "balance": 50,
            "phones": [{"type": "mobile", "status": None, "number": "2125550100"}]}
    assert select_lead(lead) is None


def test_select_lead_rejects_bad_status():
    lead = {"id": "1", "status": "closed", "state": "NY", "balance": 500,
            "phones": [{"type": "mobile", "status": None, "number": "2125550100"}]}
    assert select_lead(lead) is None
