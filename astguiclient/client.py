"""
Supabase/Postgres client + sync loop for the reference lead-sync daemon.

Placeholder implementation: `fetch_leads` returns an empty list and is intended
to be wired to a real datasource. Contains no credentials.
"""

from __future__ import annotations

from .scoring import select_lead

# This is where a real deployment reads from Supabase/Postgres. Kept as a
# stand-in so the sync loop and scoring are independently testable.
def fetch_leads() -> list[dict]:
    return []


def queue_lead(lead: dict) -> None:
    """Insert a scored lead into the dialer queue (stub)."""
    # Real implementation inserts into vicidial_list.
    pass


def sync() -> int:
    """Run one sync pass: fetch → score → queue. Returns queued count."""
    queued = 0
    for lead in fetch_leads():
        scored = select_lead(lead)
        if scored is None:
            continue
        queue_lead(scored)
        queued += 1
    return queued


if __name__ == "__main__":
    print(f"Synced {sync()} leads")
