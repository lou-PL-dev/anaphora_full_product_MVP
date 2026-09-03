# Anaphora — MVP Documentation

## 1. Purpose

Anaphora is a working AI-native matchmaking MVP for people who value depth over endless choice. Instead of starting with profile browsing and swiping, the product first helps a user articulate what matters in a relationship, structures that information into a **Relationship Blueprint**, and then uses that Blueprint to generate a small number of explainable introductions.

The MVP demonstrates the complete product loop:

**Conversation → structured Blueprint → readiness → Discoveries / friend enrichment → reciprocal retrieval → relationship reasoning → explained Intro**

Live frontend: `https://anaphora-app.netlify.app`

## 2. What the MVP demonstrates

The core AI capability actually runs end to end. The MVP is not a static prototype.

It currently supports:

- guided conversational exploration of relationship preferences and self-description;
- atomic structured extraction from conversation into three perspectives: `ME` (who the user is), `IDEAL_PARTNER` (who they want), and `US` (the relationship they want to create);
- a persisted Relationship Blueprint with `ME` categories personality, lifestyle, relationship_behavior and core_values; `IDEAL_PARTNER` categories personality, lifestyle and physical_type; and `US` categories relationship_shape, connection_affection, shared_direction and boundaries;
- source-preserving evidence: every raw observation (from conversation, a Discovery, a friend contribution, or a member's own correction) is kept, and the member-facing Blueprint is a canonical projection rebuilt from that full evidence history rather than edited signal-by-signal — see §4.2;
- a deterministic readiness score based on Blueprint coverage;
- multiple short Discoveries that add structured information and synthesized insights;
- friend contribution through single-use links, while keeping the friend's raw individual answers private from the inviting user;
- preference filters such as gender preference and age range;
- vector retrieval against a synthetic candidate pool using embeddings and pgvector;
- reciprocal fit evaluation in two directions: what the user wants versus what the candidate is, and what the candidate wants versus what the user is;
- relationship-level LLM reasoning over retrieved finalists;
- grounded match explanations shown as **Strong fit** or **Worth exploring**, with tensions surfaced where relevant;
- basic product-research event tracking and a small password-protected tester-session dashboard.

## 3. Architecture

### Frontend

- React
- Vite
- Mobile-first web application
- Hosted on Netlify

The frontend generates an anonymous UUID per browser/device and stores it in local storage. This UUID is sent to the backend in the `X-Anaphora-User-Id` header and acts as the MVP's anonymous session identity.

### Backend

- FastAPI
- SQLAlchemy
- Pydantic schemas
- Hosted on Render

The backend is organized into separate routers for conversation, Blueprint, readiness, Discoveries, matching, preferences, friends and tester-research administration.

### Database

Local development defaults to SQLite so the non-vector product flow can run with minimal setup.

The deployed matching flow uses Postgres with the pgvector extension for candidate embeddings and cosine-similarity retrieval.

Important persisted objects include:

- `User`
- `Conversation`
- `BlueprintEvidence` — raw, append-only observations from every source (conversation, Discovery, friend contribution, member correction)
- `BlueprintSignal` — the canonical, member-facing Blueprint projection rebuilt from `BlueprintEvidence` (see §4.2); never edited in place
- `DiscoveryResponse`
- `Candidate`
- `FriendInvite`
- `FriendResponse`
- `FriendSignal`
- `TesterEvent`

### AI / orchestration

- LangChain is used to construct and orchestrate LLM and embedding calls.
- OpenAI models are used for conversation, structured extraction, Discovery synthesis and relationship reasoning.
- OpenAI embeddings are used for semantic retrieval.
- LangSmith tracing can be enabled through environment variables for prompt/output inspection, latency and debugging.

OpenAI client construction is centralized in `anaphora_backend/app/llm.py` so model configuration is not duplicated across chains.

## 4. Core AI flows

### 4.1 Conversation

A user starts a guided conversation with Anaphora. The AI asks follow-up questions intended to improve coverage across both sides of the Blueprint rather than simply keeping an open-ended chat going.

Each user turn is stored as raw conversation text. The conversational layer also returns structured observations where supported by the user's words.

This separation is important: the transcript is evidence, while the structured observations become the working source of truth for later extraction and matching.

### 4.2 Relationship Blueprint extraction and canonicalization

Every Blueprint-affecting action — completing a conversation, submitting a Discovery, accepting a friend's contribution, or correcting a signal — first writes one or more raw, append-only rows to `BlueprintEvidence` (`anaphora_backend/app/blueprint_canonicalizer.py`). Evidence is never edited or deleted in place; a correction is stored as new evidence that supersedes the specific prior evidence it replaces, so the original wording is retained even after the member-facing Blueprint no longer reflects it.

The member-facing Blueprint (`BlueprintSignal`) is not built incrementally from one action at a time. Instead, `rebuild_blueprint()` sends a member's **entire active evidence history** to an LLM in one call, which merges semantic duplicates across sources, splits compound observations into independent ideas, reclassifies anything filed under the wrong lens/category, and returns one clean, non-repetitive projection. The result is validated before anything is written: every evidence ID must be grounded in at least one output signal, no signal may cite an unknown ID, and no evidence ID may be silently dropped. Only after validation passes are the old `BlueprintSignal` rows deleted and replaced — a failed or malformed canonicalization response leaves the existing Blueprint untouched rather than corrupting or emptying it.

Each canonical signal contains fields such as:

- perspective: `ME`, `IDEAL_PARTNER`, or `US`;
- category;
- label;
- strength — resolved deterministically from the linked evidence's own strength, never invented by the canonicalization model; an inferred observation can never become a `hard_requirement`, only an explicit statement or member correction can;
- source (`"canonical"`);
- the IDs of every evidence row the signal is grounded in;
- supporting evidence text;
- confidence.

A human-readable narrative describing the `IDEAL_PARTNER` is also regenerated on every rebuild, but the narrative itself is not used as a source of truth for matching.

This full-history rebuild means canonicalization cost scales with a member's total accumulated evidence, not just what changed in the current action — see `product_document/cost_timeline_estimate.md` for the measured cost shape.

### 4.3 Readiness

Readiness is deterministic rather than LLM-generated.

It reflects whether enough structured information exists across key categories and perspectives to support meaningful matching. This prevents the system from presenting candidate recommendations too early based on a thin profile.

### 4.4 Discoveries

Discoveries are short structured exercises that deepen the Blueprint after the initial conversation.

Examples explore areas such as:

- the life the user is building;
- chemistry;
- how they love;
- living together;
- non-negotiables;
- relationship patterns.

Responses are stored and then synthesized into additional Blueprint signals and insights.

### 4.5 Friend input

The user can create a limited number of single-use friend links.

A friend answers a short set of questions without creating an Anaphora account. The friend's raw answers are retained for internal extraction but are not shown verbatim to the inviting user.

The system generates a paraphrased narrative and candidate signals. These remain separate from the main Blueprint until the user explicitly reviews and accepts them.

### 4.6 RAG retrieval

Candidate profiles in the current MVP are synthetic rather than real dating users.

The matching pipeline uses vector retrieval to create a broad candidate shortlist from Postgres/pgvector. Semantic reranking then evaluates structured category evidence rather than relying only on one embedding similarity score.

This retrieval stage narrows the candidate pool. It does not itself decide whether a candidate should be shown.

### 4.7 Reciprocal matching

The matching system evaluates two directions:

1. **User wants → Candidate is**
2. **Candidate wants → User is**

This is designed to avoid a common one-sided recommendation problem where the system only asks whether a candidate fits the user's preferences.

Candidates without sufficient reciprocal evidence are downgraded or rejected from stronger fit labels.

### 4.8 Relationship reasoning and explanation

The final reasoning step examines the retrieved finalists together with grounded reciprocal evidence.

It distinguishes:

- alignment;
- complementarity;
- tension;
- incompatibility;
- reciprocity.

The model may reject a candidate entirely when evidence is too weak or contradictory. A displayed Intro is labelled **Strong fit** or **Worth exploring** rather than a numerical compatibility percentage.

The generated explanation is constrained to the evidence passed into the reasoning step.

## 5. Repository structure

```text
.
├── anaphora_backend/        FastAPI backend and AI chains
├── frontend/                React/Vite product UI
├── dashboard/               Round 1 BI dashboard
├── rag_demo/                synthetic candidate generation and ingestion
├── research/                Round 1 market/use-case research
├── product_document/        PRD, brand, pitch deck, cost work, LangSmith sample
├── feedback/                Round 1 decision / feedback notes
├── use_case_definition.md
├── mvp_documentation.md
├── .env.example
└── README.md
```

## 6. How to run locally

### Backend

```bash
cd anaphora_backend
pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn app.main:app --reload
```

The local backend defaults to SQLite.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE=http://localhost:8000` in `frontend/.env` to use the local backend. Otherwise the frontend defaults to the deployed Render backend.

### RAG candidate pool

The vector matching feature requires Postgres with pgvector and a seeded candidate table.

Typical setup:

```bash
cd rag_demo
pip install -r requirements.txt
python ingest_candidates.py -n 50
```

This requires a valid `OPENAI_API_KEY` and a `DATABASE_URL` pointing to Postgres with pgvector enabled.

## 7. Environment configuration

The root `.env.example` documents the required environment variables.

Important values include:

- `OPENAI_API_KEY`
- `DATABASE_URL`
- LangSmith tracing configuration
- `ADMIN_SECRET` for the small tester-session dashboard

Secrets must not be committed to the repository.

## 8. Basic error handling

The MVP includes basic error handling appropriate to the current testing stage:

- network/API failures return visible retry/error states rather than fabricated AI output;
- frontend API calls use timeouts;
- a cold Render backend is given longer timeouts on requests likely to trigger a server wake-up;
- matching returns a clean unavailable state when vector infrastructure is not available locally;
- no-match cases are treated as valid product outcomes rather than forced recommendations;
- friend invite links return explicit invalid / already-used states;
- tester tracking is fire-and-forget so analytics failures do not break the user flow.

The product is still an MVP and does not yet include production-grade authentication, abuse protection, observability, moderation or full operational resilience.

## 9. Testing and observability

The backend repository contains automated tests for key areas including:

- conversation / extraction behaviour;
- long-input segmentation;
- readiness and signal handling;
- matching and reciprocal reasoning;
- regression cases added during development.

LangSmith tracing can be enabled for LLM calls.

For the current small tester round, a private admin page at `/admin/test-sessions` can display anonymous tester sessions, journey events, conversations, Blueprint signals, Discovery responses and Intro activity. It is protected by a shared backend-admin secret and is intended only for internal MVP research.

## 10. Current limitations versus production

The working MVP proves the product and AI flow, but it is deliberately not production-ready.

Current limitations include:

- anonymous browser UUIDs rather than real authentication;
- synthetic candidates instead of a live two-sided dating marketplace;
- limited safety and moderation workflows;
- no identity verification;
- no messaging between matches;
- no payments;
- no production notification system;
- small-scale internal analytics rather than a full product analytics platform;
- simple shared-secret admin protection for the tester dashboard;
- architecture and prompts are still being refined based on user testing;
- deployment currently uses lightweight hosting appropriate to an MVP, including a backend that may cold-start after inactivity.

## 11. What is intentionally demonstrated

The MVP is intended to validate the following proposition:

> Rich qualitative relationship information can be converted into structured, inspectable signals and used to produce a small number of reciprocal, explainable candidate introductions rather than an endless ranked feed.

The strongest proof points in the current implementation are therefore not UI completeness or marketplace scale, but:

- real conversational AI;
- structured extraction separated from raw conversation;
- persistent Blueprint state;
- deterministic readiness;
- RAG retrieval;
- reciprocal reasoning;
- grounded explanations;
- a usable end-to-end application that external testers can try.
