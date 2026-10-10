# Predictive Dialer

A browser-based call-center dialer: agents take calls in the browser (WebRTC softphone), a supervisor dashboard shows live call state and agent activity, and a lead-sync service feeds a dialing queue with timezone-aware, scored leads.

Built around the classic open-source stack (Asterisk PBX + VICIdial) with a modern React dashboard and a small Python sync daemon.

## What it does

- **WebRTC agent phone** — browser softphone over WSS (SIP), no desk phone needed
- **Predictive dialing** — hopper-managed outbound queue that paces dials against agent availability
- **Live dashboard** — per-agent status, current lead, call duration, daily counts, leaderboard
- **Screen-pop** — surface lead context the moment a call connects
- **Lead sync** — score and queue leads with timezone-aware calling windows and dedup
- **Recordings & transcripts** — locate and serve call recordings and transcripts

## Architecture

```
Browser (JsSIP WebRTC)  ←WSS→  Asterisk PBX  ←AMI→  PHP/VICIdial app
                                                      │
                                                      ├─ MySQL (dialer state)
                                                      └─ lead_sync.py ← Supabase (Postgres)
```

## Tech stack

- Asterisk (chan_pjsip) + VICIdial 2.14
- React + TypeScript dashboard
- Node.js control API
- Python (lead sync + scoring)
- PostgreSQL / Supabase (lead data)

## Structure

```
web/
  phone/            # custom agent + call APIs
  agc/              # VICIdial agent GUI + master API
asterisk/           # dialplan + PJSIP trunk/endpoint config
astguiclient/
  lead_sync.py      # Supabase → dialer queue sync (scored, timezone-aware)
```

> This repository contains configuration templates and application code only — no credentials, recordings, or real lead data. Deployers supply their own SIP trunk and database credentials.
