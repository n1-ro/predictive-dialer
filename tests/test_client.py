import pytest

from astguiclient.client import sync, fetch_leads


def test_sync_returns_zero_with_no_leads():
    assert sync() == 0


def test_fetch_leads_returns_list():
    assert isinstance(fetch_leads(), list)
