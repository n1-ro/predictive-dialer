# Architecture

`predictive-dialer` is a reference implementation of a browser-based call-center
dialer built on the classic Asterisk + VICIdial stack.

## Topology

```
Browser (JsSIP WebRTC)  ←WSS→  Asterisk PBX  ←AMI→  PHP/VICIdial app
                                                      │
                                                      ├─ MySQL (dialer state)
                                                      └─ lead_sync (Python) ← Supabase
```

## Components

| Component | Role |
|---|---|
| `asterisk/` | Dialplan + PJSIP trunk/endpoint config (templates) |
| `web/phone/` | Custom agent + call APIs |
| `web/agc/` | VICIdial agent GUI + master API |
| `astguiclient/lead_sync.py` | Supabase → dialer queue sync |
| `astguiclient/scoring.py` | Lead/phone scoring + gates |
| `astguiclient/timezone.py` | Timezone-aware dialing windows (DST-aware) |
| `astguiclient/client.py` | Sync loop + queue insertion |

## Lead sync flow

```
fetch_leads() ──► select_lead()  (status/balance/phone gates + scoring)
                        │
                        ▼
              queue_lead() ──► vicidial_list
```

`select_lead()` rejects leads outside dialable hours, below minimum balance,
with bad phone statuses, or with no usable phones — then ranks them and picks
the best phone. `timezone.py` computes per-state local hours with DST awareness.

> No credentials or real lead data are included anywhere in this repository.
