# Use Case Proposals — Anaphora (Startup, 5-8 people)

Company-size framing: as a pre-seed startup, Anaphora cannot build custom
ML infrastructure or hire a data science team. Every use case below is
scoped to be buildable with foundation-model APIs, off-the-shelf
embeddings/vector search, and a small engineering team — this is
precisely the gap an AI consultant helps a founder like Chleo close.

## Use Case 1: AI-Native Self-Discovery & Profile Extraction
**What it does:** Instead of a single "personality test," users move
through short, scenario-based "Discoveries" (2-5 minutes each) —
situational choices and forced trade-offs rather than abstract rating
scales — covering distinct dimensions (emotional needs, life priorities,
attraction, relationship dynamics, lifestyle, dealbreakers). A
conversational AI layer (text or voice) lets users elaborate in their own
words ("think of three people you've been intensely attracted to — what
did they have in common?"), and an LLM chain extracts structured profile
data from both the choices and the free-form answers.

**Why it fits a startup:** No custom NLP model needed — LangChain + a
hosted LLM + a Pydantic schema handles the extraction in days, not
months. The Discoveries themselves are structured UI flows, not ML
artifacts.

**Business impact:** Higher-quality, multi-dimensional preference data
than a single static form or personality score; the discovery framing
("understand yourself, understand what you need") is itself a
differentiator that fits the loneliness/authenticity positioning, and
reduces onboarding drop-off versus a long questionnaire.

**MVP scope note:** Round 1's POC builds one representative Discovery
(scenario/trade-off flow) plus the conversational free-text intake — not
the full seven-discovery set described in product design docs. The
Round 2 roadmap can scope 3 short Discoveries + conversational intake as
the fuller MVP slice.

## Use Case 2: Explainable, Multi-Source Matching Engine
**What it does:** Candidate profiles are embedded and compared via
similarity search; an LLM generates a plain-language explanation of *why*
two profiles were matched, alongside a compatibility signal. Where a
friend's input is available, the engine compares three perspectives per
trait — what the user says, what their own choices/patterns reveal, and
what a friend observes — and flags convergence (strong signal) versus
divergence (worth exploring) rather than presenting one flattened score.

**Why it fits a startup:** Embeddings + a local vector DB (Chroma/FAISS)
are free/cheap to run at small scale — no proprietary ML required for a
credible v1. The three-perspective comparison is a data-modeling choice
(structuring the same dimensions across sources), not new ML.

**Business impact:** Directly addresses Chleo's "AI must be transparent"
concern — every match ships with a human-readable rationale grounded in
what was actually said, not a black-box score. This is a stronger,
harder-to-copy differentiator than "AI matching" alone, since it depends
on having the friend-input data pipeline (Use Case 3) in place.

## Use Case 3: Friend Perspective Intake ("Ask someone who knows you")
**What it does:** Users invite 1-3 friends via a no-install, no-account
mobile webpage. Friends answer a short set of playful, structured
questions about the user (text or voice), including a natural
conversational close ("imagine you're setting them up with someone — tell
Anaphora about that person") that an LLM maps back to the same structured
relationship dimensions used in Use Case 1.

**Why it fits a startup:** Reuses the same LangChain extraction chain
from Use Case 1 — no separate infrastructure. The friction-free,
no-account design keeps friend participation high without extra backend
complexity (auth, accounts) for a party who isn't even the paying user.

**Business impact:** This is Anaphora's most defensible differentiator
versus existing "friend-assisted" dating products (e.g. Wingman), which
only vouch/swipe rather than feeding structured data into matching. It's
also a natural, low-cost growth loop — every user who completes onboarding
is a source of 1-3 new visitors to the product.

**Priority for POC/MVP:** Use Cases 1 and 2 form the Round 1 working
demo (one Discovery + conversational intake + embedding-based matching
with an LLM-generated explanation). Use Case 3 (friend intake) is
documented as the differentiator and prioritized for Round 2's MVP, once
the core intake-to-match pipeline is proven — keeps Round 1's POC scoped
to "one capability that runs end to end," per the rubric.
