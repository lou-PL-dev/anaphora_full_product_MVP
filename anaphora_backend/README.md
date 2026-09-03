# Anaphora — MVP Backend

FastAPI backend for the technical MVP described in
`Anaphora__MVP_Product_Requirements_Document.md`. Paired with the React
frontend in `../frontend/` — see "Connecting the frontend" below, and the
repo-root README for how the two are deployed together (Render + Netlify).

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
│   ├── blueprint_canonicalizer.py # raw evidence → deduplicated Blueprint projection
│   ├── chains/
│   │   ├── conversation_chain.py     # Operation A — the ideal-partner conversation
│   │   ├── extraction_chain.py        # Operation B — structured extraction
│   │   ├── discovery_chain.py          # the one MVP Discovery + its insight synthesis
│   │   └── matching_chain.py            # Operation C — RAG matching (retrieval + generation)
│   └── routers/
│       ├── conversation_router.py    # /conversation/start, /message, /complete
│       ├── blueprint_router.py        # /blueprint, /blueprint/signal/{id}
│       ├── readiness_router.py         # /readiness
│       ├── discovery_router.py          # /discovery/{id}, /discovery/{id}/respond
│       └── matching_router.py            # /matches
├── test_flow.py                        # end-to-end test of the full PRD demo scenario
├── canonicalize_blueprints.py          # one-time cleanup for existing profiles
├── test_duplicate_fix.py               # regression test for the re-completion duplicate-signals bug
├── test_matching.py                    # matching chain + router tests (mocked LLM, no real Postgres needed)
├── requirements.txt
└── README.md
```

Note: every file in `chains/` and `routers/` has a unique name across the
whole project (e.g. `chains/conversation_chain.py` vs.
`routers/conversation_router.py`), so downloading files individually into
the same folder can't silently overwrite one with another.

## Setup
```bash
pip install -r requirements.txt
cp ../.env.example ../.env   # repo-root .env — see ../.env.example; paste your real OPENAI_API_KEY
uvicorn app.main:app --reload
```
API docs (auto-generated): http://localhost:8000/docs

Defaults to a local SQLite file (`anaphora.db`, created automatically on
first run) — no database setup needed to try it. For real use, set
`DATABASE_URL` in `.env` to a real Postgres connection string (the
deployed instance uses Render Postgres); every model in `app/models.py`
is plain SQLAlchemy and works unchanged either way.

## Cleaning existing Blueprints after this upgrade

New conversations, Discoveries, accepted friend contributions, and member
corrections now preserve their raw evidence and rebuild one canonical
Blueprint. This semantically merges paraphrases, splits compound ideas,
reclassifies misplaced ideas, and replaces rather than appends the
ideal-partner portrait.

After deploying the schema update, run this once from `anaphora_backend/`
with `DATABASE_URL` and `OPENAI_API_KEY` pointing at the intended database:

```bash
python canonicalize_blueprints.py --all
```

To clean only one profile, use `--user-id <uuid>`. Each profile is committed
independently; a failed model response leaves that profile's current Blueprint
unchanged and the command reports the failure.

Note: `Base.metadata.create_all()` only creates tables that don't already
exist — it never alters an existing table. If you pull a change that adds
a column (e.g. `User.blueprint_narrative`) and hit a "column does not
exist" error against a database you'd already run before, drop and
recreate the schema rather than just restarting: `DROP SCHEMA public
CASCADE; CREATE SCHEMA public;` in `psql`, then restart the app.

## RAG matching (`/matches`)
Retrieves synthetic candidate profiles whose own self-description is close
to the user's `ideal_partner` Blueprint (pgvector cosine similarity, used
only to rank/shortlist internally), then an LLM honestly judges — per
candidate — whether there's something genuine and specific to say, in
Anaphora's own PRD-specified style (section 26, Match Presentation): no
numeric score is ever shown, just **Strong fit** / **Worth exploring** plus
themed prose sections ("The life you're building", "How you connect", an
honestly-named tension under "Something to explore", etc.) —
`chains/matching_chain.py`. A candidate with nothing genuine gets dropped
entirely rather than shown with generic filler text; `/matches` can
legitimately return fewer than the shortlist size, including zero — "depth
over volume" per the PRD's own Product Principles, not a bug.

`/matches` also gates on real readiness: it calls `readiness.compute_readiness`
and returns `{ready: false, matches: []}` below 100% (the frontend sends the
user back to finish the conversation rather than showing an empty or
misleading Matches screen), and `{ready: true, matches: []}` when ready but
nothing in the pool currently clears the genuineness bar (frontend shows
"We're still curating profiles for you").

Candidates are NOT real users — they're generated by
`rag_demo/generate_personas.py`'s self-profile mode and seeded via
`rag_demo/ingest_candidates.py` (see that file and
`rag_demo/dataset_documentation.md`).

Requires:
- **Postgres with pgvector** — run `CREATE EXTENSION IF NOT EXISTS vector;`
  once against your Postgres instance (same `psql` connection you'd use for
  a schema reset — see above). Local SQLite dev does not support this
  feature at all: the `candidates` table is skipped on `create_all()` (see
  `app/main.py`), and `/matches` returns a clean `503` rather than crashing.
- Candidate photos in `frontend/public/candidates/` (served as static
  frontend assets — see that folder's README) — candidates without one
  fall back to an initials avatar in the UI.
- Seeding the pool: `cd rag_demo && python ingest_candidates.py -n 50`
  (needs `OPENAI_API_KEY` + `DATABASE_URL` pointing at the real Postgres
  instance — generates narratives, runs them through the real extraction
  chain, computes embeddings, writes to `candidates`).

## LangSmith tracing (optional)
Every LLM call goes through LangChain (`ChatOpenAI` in `chains/conversation_chain.py`,
`chains/extraction_chain.py`, `chains/discovery_chain.py`), so tracing needs
no code changes — just set these in `.env` (see `../.env.example`):
```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<your LangSmith API key>
LANGCHAIN_PROJECT=anaphora-mvp
```
Every conversation turn, Blueprint extraction, and Discovery insight then
shows up as a trace in your LangSmith project — the exact prompt sent, the
structured output returned, latency, and token cost. `rag_demo/generate_personas.py`
runs real transcripts through `extract_blueprint` too, so it's a quick way
to generate a batch of traces without going through the chat UI by hand.

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
section 5). CORS is wide open (`allow_origins=["*"]`) so a localhost or
deployed frontend can call it without extra config — tighten this in
`app/main.py` before anything resembling production.

The frontend in `../frontend/` defaults to calling the deployed Render
backend (see `frontend/src/api.js`) — set `VITE_API_BASE` in
`frontend/.env` to point it at `http://localhost:8000` for local dev
against this backend instead.

## Endpoint summary
| Endpoint | Maps to |
|---|---|
| `POST /conversation/start` | §6-7, opens the chat with the fixed opening prompt |
| `POST /conversation/message` | §8-9 (Operation A), one turn of the matchmaker conversation |
| `POST /conversation/complete` | §10-13 (Operation B), extracts signals + a narrative portrait, stores the Blueprint |
| `GET /blueprint` | §14, the Blueprint review screen — signals + the narrative portrait |
| `PATCH /blueprint/signal/{id}` | §14, "Change something" |
| `GET /readiness` | §16-17, deterministic readiness % |
| `GET /discovery/{id}` | §4F, fetches the one MVP Discovery's questions |
| `POST /discovery/{id}/respond` | §4F/§37, stores responses, synthesizes the insight, updates readiness |
| `GET /matches` | RAG matching against the synthetic candidate pool — see "RAG matching" below |

## What's deliberately not here (PRD section 5)
Real matchmaking/recommendation, vector search, payments, production
auth, identity verification, moderation, real friend-contribution
processing, notifications. The Friends and Matches tabs are frontend-only
static content per the PRD — no backend endpoints needed for them yet.
