# Anaphora

An AI matchmaking MVP: instead of swiping, a user has one guided conversation
about the partner they'd love to meet, an AI extracts a structured
**Relationship Blueprint** from it (plus a written, human-readable portrait),
and a deterministic **readiness score** tracks how complete that picture is.
See `PRDs/Anaphora_Vision_Product_Requirements Document.md` for the full
product spec this MVP implements against.

**Live**: [anaphora-app.netlify.app](https://anaphora-app.netlify.app) (frontend) ·
backend on Render (spins down after ~15 min idle on the free tier — the
first request after that can take up to ~50s to wake up).

## Repository structure

```
.
├── anaphora_backend/   FastAPI backend — conversation, extraction, readiness, discovery
├── frontend/            React frontend (Vite) — the mobile app UI, deployed to Netlify
├── dashboard/            BI dashboard (FastAPI + vanilla JS) — market + product metrics
├── rag_demo/              Synthetic trait-grounded Blueprint dataset generator (RAG demo)
├── research/               Sector research, opportunities/risks, use cases
├── PRDs/                    Product requirements document
├── Anaphora_brand.png        Brand sheet (palette, type, tone) the UI is built from
├── .env.example               Shared env vars — see below for where each component reads it from
└── README.md                   This file
```

## Setup

Copy `.env.example` and fill in real values — **never commit the copy**.
Each component reads its `.env` from a different place (see the comments
inside `.env.example` for exactly why):

```bash
cp .env.example .env             # anaphora_backend reads this, from the repo root
cp .env.example dashboard/.env   # dashboard reads its own copy
```

### Backend (`anaphora_backend/`)
```bash
cd anaphora_backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Runs on `http://localhost:8000`, auto-docs at `/docs`. Defaults to a local
SQLite file — no database setup needed to try it. Full details, endpoint
list, and how to verify it works without an OpenAI key (`test_flow.py`):
see `anaphora_backend/README.md`.

### Frontend (`frontend/`)
```bash
cd frontend
npm install
npm run dev
```
Runs on `http://localhost:5173`, and defaults to calling the **deployed**
Render backend — set `VITE_API_BASE=http://localhost:8000` in
`frontend/.env` to point it at your local backend instead.

### BI Dashboard (`dashboard/`)
```bash
cd dashboard
pip install -r requirements.txt
uvicorn dashboard_api:app --reload
```
Open `http://localhost:8000`. Metrics rationale, sources, and navigation:
`dashboard/dashboard_documentation.md`; screenshots in `dashboard/screenshots/`.

### Synthetic dataset generator (`rag_demo/`)
```bash
cd rag_demo
pip install -r requirements.txt  # plus ../anaphora_backend/requirements.txt — see rag_demo/requirements.txt
pytest                            # runs offline, no API key needed
python generate_personas.py -n 20 # the real LLM-backed pipeline, needs OPENAI_API_KEY
```
What this generates and why, full sourcing for the trait distributions it
samples from: `rag_demo/dataset_documentation.md`.

## Round 1 deliverables — where to find each one

| # | Deliverable | Where |
|---|---|---|
| 1 | Repo structure, `requirements.txt`, `.env.example`, commit history | This file; `anaphora_backend/requirements.txt`, `rag_demo/requirements.txt`; root `.env.example`; git log |
| 2 | Research pack | `research/sector_research.md`, `research/opportunities_risks.md`, `research/use_cases.md` |
| 3 | BI Dashboard | `dashboard/` — custom FastAPI + JS dashboard (agreed alternative to PowerBI); `dashboard/dashboard_documentation.md` + `dashboard/screenshots/` |
| 4 | Automation POC (n8n) | Not included — confirmed optional for this project |
| 5 | LangSmith monitoring sample | See `anaphora_backend/README.md` / `.env.example` for how tracing is wired in (`LANGCHAIN_TRACING_V2` etc.) |
| 6 | Cost & timeline estimate | *In progress* |
| 7 | Round 1 presentation + decision | *Pending — presentation not yet given* |

## Tech stack

FastAPI + SQLAlchemy + Postgres (Render) / SQLite (local) · LangChain +
OpenAI (`gpt-4o-mini`) for the three LLM call sites (conversation,
structured extraction, Discovery insight synthesis) · React + Vite,
deployed to Netlify · plain FastAPI + vanilla JS for the dashboard.
