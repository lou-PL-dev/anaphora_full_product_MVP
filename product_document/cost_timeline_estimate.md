# Anaphora — Cost & Timeline Estimate

## Timeline — Round 2 (this week)

Round 1 presented Monday morning. Round 2 demos Friday.

| Day | Milestone | What happens |
|---|---|---|
| Mon AM | Round 1 recap | What's live right now: self-tracking conversational intake, the 7-category Relationship Blueprint with a narrative portrait, one working Discovery, and the sourced market dashboard — everything in this demo. |
| Mon PM | Round 2 kickoff | Clean datasets of profiles, and build the RAG matching logic. Start the friend-invite feature and link. |
| Tue | Friends end-to-end + real matching | Friend signals land on the asker's Blueprint with `source=friend` provenance. `matching_chain` embeds profile narratives and writes the "why this match" rationale. Recruit testers for Wednesday. |
| Wed | User testing, then react | Real people run the conversation and the friend-invite flow end to end. Log every drop-off and confusing moment; fix the top issues the same day. |
| Thu | Regression, polish, rehearse | Full end-to-end pass, mobile check on the public friend page, docs updated to reflect what's real vs. next, demo rehearsal. |
| Fri | Final presentation | Round 2 demo — plus what was learned from testing with real people, not just more features. |

**By Friday**: conversation → Blueprint → readiness → RAG matching → friend-contributed signals, tested end-to-end with real people, not just synthetic data.

## Cost estimate

### Methodology

`cost_estimate/cost_model.py` computes this from two kinds of input, kept
strictly separate so the estimate is auditable:

1. **Measured**: character counts of the actual system prompts shipped in
   `anaphora_backend` — imported directly from the real chain modules
   (`conversation_chain.SYSTEM_PROMPT`, `extraction_chain.EXTRACTION_SYSTEM_PROMPT`,
   `discovery_chain.SYNTHESIS_SYSTEM_PROMPT`, `matching_chain.MATCH_SYSTEM_PROMPT`),
   not paraphrased or guessed at. Converted to an approximate token count
   (~4 chars/token, OpenAI's own published rule of thumb) — exact BPE
   tokenization via `tiktoken` needs a vocab file from a host this sandboxed
   dev environment's network policy blocks, so this is an approximation,
   not exact. Once real conversations are happening, LangSmith's traces
   (already wired in — see `anaphora_backend/README.md`) report **exact**
   real token usage per call and should replace this approximation.
2. **Assumed**: everything that varies per real user (message length,
   conversation length) — no production traffic exists yet to measure this
   from, so these are explicit, labeled guesses in `ASSUMPTIONS` at the top
   of the script, not hidden inside the math. Change them and rerun to see
   how sensitive the estimate is.

Pricing sourced via web search against aggregator pricing pages
(cloudzero.com, lmmarketcap.com, openrouter.ai) on 2026-08-31 — OpenAI's own
pricing page was not directly reachable from this dev environment to
cross-check against. **Spot-check against platform.openai.com/docs/pricing
before treating this as final.**

Reproduce: `cd product_document/cost_estimate && python cost_model.py`

### Per-user-journey cost (one conversation + extraction + one Discovery + one `/matches` call, 6 turns assumed)

| Call | Model | Cost |
|---|---|---|
| Conversation | `gpt-4o` | $0.02098 |
| Extraction | `gpt-4o-mini` | $0.00051 |
| Discovery insight | `gpt-4o-mini` | $0.00004 |
| Matching (embed + explain) | `text-embedding-3-small` + `gpt-4o-mini` | $0.00017 |
| **Total** | | **$0.0217** |

**Key finding**: the conversation dominates cost (~97% of the journey) for
two compounding reasons — it's the one call site on the pricier `gpt-4o`
(needed to actually track category coverage across a transcript reliably,
see the earlier prompt-quality fix), and `conversation_chain._to_langchain_messages`
resends the **entire message history every turn**, so input tokens grow
roughly with the square of turn count, not linearly. A 12-turn conversation
(the hard ceiling) costs meaningfully more than double a 6-turn one — worth
knowing if usage grows and this needs optimizing (e.g. summarizing older
turns instead of resending them verbatim).

### One-time cost: seeding the candidate pool

`rag_demo/ingest_candidates.py` — narrative + extraction + embedding per
synthetic candidate: **$0.0022/candidate** → 50 candidates ≈ **$0.11 total**,
paid once, not recurring per user.

### Fixed hosting costs

Computed in the same script (`HOSTING` dict), not a separate hand-typed
table — sourced via web search (Render/Netlify's own pricing pages are
JavaScript-rendered and couldn't be fetched directly from this
environment), so spot-check against render.com/pricing and
netlify.com/pricing before final submission.

| Service | Free tier (current) | Paid tier (if scaling) |
|---|---|---|
| Render web service (backend) | $0 — spins down after ~15 min idle, ~50s cold start on wake | Starter, $7/mo — always-on, no cold start |
| Render Postgres | $0 — **expires 30 days after creation**, needs monitoring or an upgrade before Round 2 demo week is out | Basic-256mb, $6/mo |
| Netlify (frontend) | $0 — credit-based since April 2026 (300 credits/mo, no auto-recharge on exhaustion) | Pro, $20/mo — see "Paris pilot" below for why Pro, not the cheaper Personal tier |
| **Total** | **$0/mo** | **$33/mo** |

### Total monthly cost at different scales (LLM + hosting)

| New users/month | LLM only | + free-tier hosting | + paid-tier hosting |
|---|---|---|---|
| 100 | $2.17 | $2.17 | $35.17 |
| 1,000 | $21.70 | $21.70 | $54.70 |
| 10,000 | $216.96 | $216.96 | $249.96 |

At current (near-zero) usage, hosting is the dominant cost, not LLM calls
— that inverts somewhere between 1,000 and 10,000 new users/month, per
the table above. The $33/mo paid-tier floor is worth budgeting for
regardless of LLM volume: it buys an always-on backend (no cold-start
demo risk) and a Postgres instance that doesn't silently expire.

### Paris pilot — will the free tiers actually hold up?

Rather than guess a pilot traffic number, `pilot_scenario()` in the same
script answers this from data that's actually real: measured file sizes
in this repo, and this repo's own git history.

**Bandwidth is fine.** Netlify's free tier gives ~15GB/month. A repeat
visitor's session costs the gzipped JS+CSS bundle (61KB, from the actual
`npm run build` output) plus however many real candidate photos they see
— only 10 of the 50 seeded candidates have a real photo today (the rest
render a free initials avatar), so a 5-match `/matches` response shows
~1 real photo on average (206KB, the actual average size of the 10 files
in `frontend/public/candidates/`). That's ~267KB/session — **~59,000
sessions before the free bandwidth pool runs out.** Not the constraint.

**Deploy credits are the real constraint.** The same 300 credits/month
also pays for production deploys — 15 credits each, ~20 deploys/month.
Netlify auto-deploys on every push to `main` that touches `frontend/` by
default. This repo's own commit history over the last 2 days: **16
frontend-touching commits, ~8/day.** At that pace, the free tier's
20-deploy budget is gone in **~2.5 days** — not from real user traffic at
all, just from active development. This is the actual argument for
upgrading Netlify before a live pilot, not bandwidth: **Pro ($20/mo, 3,000
credits ≈ 200 deploys/month)** gives real headroom at this dev pace;
Personal ($9/mo, ~66 deploys/month) would still run out mid-pilot-week if
development stays this active.

### Other operational costs for a real pilot

`OTHER_COSTS` in the script is deliberately structured to be extended —
analytics is the first, concrete line item, added the way any future one
would be:

| Cost | Why | Price |
|---|---|---|
| Plausible Analytics (Starter) | EU-hosted, privacy-first, no cookie banner needed — matches the app's own "Privacy by design · EU-first" positioning better than a US-based analytics vendor would for a Paris pilot. Up to 10k pageviews/mo. | $9/mo |

### Paris pilot fixed monthly floor

| | Cost |
|---|---|
| Hosting (paid tier) | $33.00 |
| Plausible Analytics | $9.00 |
| **Fixed monthly floor** | **$42.00** |
| + per-user-journey LLM cost on top | + $0.0217 × new users that month |

E.g. a 300-signup first pilot month: $42 fixed + (300 × $0.0217) ≈ **$48.51
total** — hosting and analytics dominate at this scale, not LLM calls.

### Assumptions log (everything not measured from real code)

| Assumption | Value | Basis |
|---|---|---|
| Avg. user turns/conversation | 6 | Midpoint of the 3–12 turn range enforced in `conversation_chain.py`; no production data yet |
| Avg. user message length | 40 tokens (~30 words) | Rough estimate from testing transcripts |
| Avg. AI reply length | 45 tokens | Matches the "one or two sentences" prompt rule |
| Extraction output size | 600 tokens | Two full Blueprints + narrative, structured |
| Matches returned per request | 5 | Default `k` in `matching_router.get_matches` |

### Caveats

- Pricing not cross-checked against OpenAI's own pricing page (network
  restriction in this dev environment) — verify before final submission.
- Token counts are a character-count approximation, not exact BPE — real
  LangSmith traces will supersede this once there's real conversation
  volume.
- No real usage data exists yet — every per-user assumption above is a
  labeled guess pending Wednesday's user testing session, which is exactly
  the point of that session: replace these guesses with real numbers.
- The deploy-credit finding assumes Netlify is configured to auto-deploy
  on every push to `main` (its default) — if a build filter/ignore rule is
  already configured, the real number of deploys/month could be lower.
  Worth checking directly in the Netlify dashboard's build settings.
- The "~8 frontend commits/day" pace reflects active initial development
  (today's session), not necessarily the steady-state rate during Round 2
  or after — could be higher during the Tue–Thu build/testing sprint, or
  lower once things stabilize.
