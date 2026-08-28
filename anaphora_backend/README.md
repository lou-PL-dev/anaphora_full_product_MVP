# Anaphora — MVP Backend

FastAPI backend for the technical MVP described in
`Anaphora__MVP_Product_Requirements_Document.md`. Built for a Claude
Design frontend to call directly — see "Connecting the frontend" below.

## Folder structure
```
anaphora_backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, router registration
│   ├── config.py             # settings (.env loading)
│   ├── database.py           # SQLAlchemy engine/session
│   ├── models.py              # ORM models (PRD section 33)
│   ├── schemas.py              # Pydantic request/response + LLM extraction schema
│   ├── auth.py                  # anonymous session dependency (no real auth, PRD section 5)
│   ├── readiness.py              # deterministic readiness % (PRD section 17)
│   ├── chains/
│   │   ├── conversation_chain.py     # Operation A — the ideal-partner conversation
│   │   ├── extraction_chain.py        # Operation B — structured extraction
│   │   └── discovery_chain.py          # the one MVP Discovery + its insight synthesis
│   └── routers/
│       ├── conversation_router.py    # /conversation/start, /message, /complete
│       ├── blueprint_router.py        # /blueprint, /blueprint/signal/{id}
│       ├── readiness_router.py         # /readiness
│       └── discovery_router.py          # /discovery/{id}, /discovery/{id}/respond

Note: every file in `chains/` and `routers/` has a unique name across the
whole project (e.g. `chains/conversation_chain.py` vs.
`routers/conversation_router.py`), so downloading files individually into
the same folder can't silently overwrite one with another.
├── test_flow.py                        # end-to-end test of the full PRD demo scenario
├── requirements.txt
├── .env.example
└── README.md
```

## Setup
```bash
pip install -r requirements.txt
cp .env.example .env   # paste your real OPENAI_API_KEY
uvicorn app.main:app --reload
```
API docs (auto-generated): http://localhost:8000/docs

Defaults to a local SQLite file (`anaphora.db`, created automatically on
first run) — no database setup needed to try it. For real use, set
`DATABASE_URL` in `.env` to a Supabase Postgres connection string; every
model in `app/models.py` is plain SQLAlchemy and works unchanged.

## Verify it works without an OpenAI key
```bash
python test_flow.py
```
Runs the full PRD section 37 demo scenario (conversation → extraction →
Blueprint → readiness → Discovery → readiness increase → signal
correction) against a real SQLite DB, with the three LLM call sites
mocked — confirms the whole data flow and readiness logic before you
spend API credits on it.

## Connecting the frontend
Every endpoint expects a header:
```
X-Anaphora-User-Id: <a UUID your frontend generates once and stores locally>
```
No login flow — the backend upserts a `users` row on first sight of a
given ID (see `app/auth.py` for why this is enough for an MVP per PRD
section 5). CORS is wide open (`allow_origins=["*"]`) so a Claude Design
preview or localhost frontend can call it without extra config — tighten
this in `app/main.py` before anything resembling production.

## Endpoint summary
| Endpoint | Maps to |
|---|---|
| `POST /conversation/start` | §6-7, opens the chat with the fixed opening prompt |
| `POST /conversation/message` | §8-9 (Operation A), one turn of the matchmaker conversation |
| `POST /conversation/complete` | §10-13 (Operation B), extracts + stores the Blueprint |
| `GET /blueprint` | §14, the Blueprint review screen |
| `PATCH /blueprint/signal/{id}` | §14, "Change something" |
| `GET /readiness` | §16-17, deterministic readiness % |
| `GET /discovery/{id}` | §4F, fetches the one MVP Discovery's questions |
| `POST /discovery/{id}/respond` | §4F/§37, stores responses, synthesizes the insight, updates readiness |

## What's deliberately not here (PRD section 5)
Real matchmaking/recommendation, vector search, payments, production
auth, identity verification, moderation, real friend-contribution
processing, notifications. The Friends and Matches tabs are frontend-only
static content per the PRD — no backend endpoints needed for them yet.
