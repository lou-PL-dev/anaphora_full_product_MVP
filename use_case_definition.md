# Anaphora — Use Case Definition

## 1. Business problem

Online dating products are optimized around large pools, profile browsing, and repeated swiping. This creates abundant choice, but often provides weak support for a harder problem: helping people articulate what actually matters to them in a relationship and identifying matches that make sense for both people.

Users may know that a profile is attractive or interesting, but still struggle to answer questions such as:

- What kind of relationship dynamic works for me?
- Which preferences are important versus merely familiar?
- What patterns from past relationships should influence future choices?
- Does this person fit what I am looking for — and do I fit what they are looking for?

For a new matchmaking product, this creates a product and business challenge. Matching quality cannot depend only on demographic filters or profile similarity. The system needs richer, structured relationship context while remaining understandable, privacy-conscious, and useful to the user.

Anaphora addresses this by replacing swipe-first discovery with a conversational Relationship Blueprint that progressively captures both **who the user is** and **who may suit them**, then uses those signals to generate a small number of explainable introductions.

## 2. Company profile

**Company:** Anaphora  
**Industry:** Consumer dating / relationship technology  
**Stage:** Fictional early-stage / pre-seed startup  
**Team size:** Approximately 5–8 people  
**Primary market:** European users  
**Product model:** AI-native matchmaking platform

### Current state

Anaphora is being developed as a working MVP rather than a traditional swipe-based dating application. The current product includes:

- an AI-guided conversation about the user's ideal relationship and partner;
- a structured Relationship Blueprint containing signals about both the user (`ME`) and their desired partner (`IDEAL_PARTNER`);
- progressive self-discovery questionnaires (“Discoveries”);
- optional friend input, with the friend's raw answers kept private from the inviting user;
- a deterministic readiness model indicating when enough information has been collected for matching;
- retrieval and reciprocal compatibility reasoning against a synthetic candidate pool;
- grounded match explanations presented as “Strong fit” or “Worth exploring” rather than opaque compatibility percentages.

The live MVP is available at `https://anaphora-app.netlify.app`.

## 3. Proposed AI solution

### Solution

Anaphora uses conversational and generative AI to turn qualitative relationship information into a structured, progressively enriched representation called the **Relationship Blueprint**.

The AI system performs several distinct tasks:

1. **Conversational exploration** — asks follow-up questions and helps the user articulate preferences, values, relationship dynamics, lifestyle, attraction and dealbreakers.
2. **Structured extraction** — converts conversational evidence into atomic Blueprint signals rather than treating the chat transcript itself as the matching profile.
3. **Discovery synthesis** — turns answers to short structured exercises into additional insights and signals.
4. **Retrieval-augmented matching** — uses embeddings and pgvector to retrieve potentially relevant candidate profiles from a candidate pool.
5. **Reciprocal compatibility reasoning** — evaluates two directions: whether the candidate fits what the user wants and whether the user fits what the candidate wants.
6. **Explainable introduction generation** — produces a grounded explanation of why a match may be worth exploring, including tensions where relevant, instead of exposing a black-box numerical score.

### System type

The MVP is a **human-facing generative AI recommendation and decision-support system** combining:

- LLM-based conversation;
- structured information extraction;
- deterministic business logic;
- embeddings and vector retrieval (RAG);
- LLM-based relationship reasoning over retrieved finalists.

The AI does not autonomously make consequential decisions for users. It proposes and explains introductions; the user remains responsible for whether to engage with another person.

## 4. Key stakeholders and interests

| Stakeholder | Primary interests |
|---|---|
| Users seeking a partner | Relevant introductions, psychological safety, understandable reasoning, control over their data and preferences |
| Potential matches / future marketplace participants | Reciprocal relevance, fair representation, avoidance of misleading or one-sided matching |
| Friends contributing input | Clear consent, limited effort, privacy of their individual responses |
| Product team | Evidence that richer conversational data improves activation, profile quality and match usefulness |
| Engineering / AI team | Reliable structured outputs, observable AI behaviour, manageable latency and cost, reproducible matching logic |
| Founder / investors | Product differentiation, retention potential, scalable unit economics, credible compliance posture |
| Regulators / privacy stakeholders | Lawful data processing, transparency, data minimisation, user rights, appropriate AI governance |

## 5. Success criteria

The MVP should demonstrate that users can move from an open conversation to a structured, usable matchmaking representation and receive an introduction they understand.

Initial measurable success criteria for pilot testing are:

1. **Blueprint completion:** at least 70% of testers who start the first conversation create a Relationship Blueprint.
2. **Meaningful enrichment:** at least 60% of testers who create a Blueprint complete at least one Discovery or add further information after the initial conversation.
3. **Match explanation usefulness:** at least 70% of testers who receive an Intro rate the explanation as understandable and grounded in what they shared.
4. **Technical reliability:** at least 95% of core MVP actions (conversation turn, Blueprint creation, Discovery submission and Intro retrieval) complete without an unhandled application error during the pilot.

These are pilot targets rather than validated commercial benchmarks. They will be adjusted once a larger set of real user behaviour is available.

## 6. Out of scope

The current MVP deliberately does not attempt to deliver the complete production dating marketplace.

Out of scope for this stage:

- a large pool of real dating users;
- production-grade identity verification and authentication;
- payments and subscription billing;
- messaging between matched users;
- safety moderation and trust-and-safety operations at marketplace scale;
- production ranking experimentation and large-scale recommendation optimization;
- guarantees that a recommended relationship will be successful;
- psychological or clinical assessment;
- autonomous decisions about who a user may or may not date.

The candidate pool used for the current matching demonstration is synthetic. This allows the matching and explanation architecture to be tested without representing synthetic profiles as real people.

## 7. Evolution from Round 1

The industry and core use case did **not** change after the Round 1 presentation. Teaching feedback was positive and the direction was continued.

The main evolution has been technical and product depth:

- The Round 1 concept focused on conversational AI for richer matchmaking and a Relationship Blueprint.
- A teaching suggestion was to separate information extraction from conversational response generation, for example by extracting important information into structured JSON before later reasoning. The current architecture now follows this principle: atomic observations and structured Blueprint signals are persisted separately from the conversational transcript and are the source of truth for later matching.
- RAG matching had not yet been implemented at Round 1. It is now part of the working MVP using OpenAI embeddings, Postgres/pgvector and a synthetic candidate pool.
- Matching has evolved beyond one-direction similarity. The current implementation evaluates reciprocal fit in both directions and then applies a relationship-level reasoning step to the retrieved finalists.
- Discoveries and friend input were added to enrich the Blueprint beyond the initial conversation.
- The project has moved from a concept/prototype direction into a deployed end-to-end MVP that can be tested by external users.

The core thesis remains the same: **depth over endless choice, with AI that explains rather than simply predicts.**
