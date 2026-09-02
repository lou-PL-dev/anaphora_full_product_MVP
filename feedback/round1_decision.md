# Round 1 Feedback & Decision

## Feedback received

The Round 1 presentation was positively received overall, with no major change of direction requested.

Key points from the teaching feedback:

- The custom-built dashboard was accepted as an appropriate alternative to Tableau / Power BI for this project and can remain part of the final submission.
- A suggestion was made to improve the AI conversation architecture by separating the extraction of relevant information from conversational response generation — for example, first extracting important information into a structured JSON-like representation before using it for later follow-up questions, summaries or reasoning.
- RAG-based matching had not yet been implemented at the time of the Round 1 presentation. I indicated that I planned to explore it and provide an update on the implementation.
- Overall feedback on the chosen use case, product direction and Round 1 work was positive: continue developing the same project rather than changing industry or use case.

## How the feedback was addressed

The architecture has evolved substantially since Round 1 and now follows the suggested separation between conversation and structured state.

The current MVP:

- stores the raw conversation as evidence;
- extracts atomic structured observations from user input;
- reconciles those observations into persisted Relationship Blueprint signals;
- uses those structured signals, rather than the chat transcript alone, as the source of truth for readiness and matching;
- keeps narrative summaries as a human-readable projection rather than the only representation of user preferences.

This means the main architectural suggestion from Round 1 has effectively been incorporated into the later implementation.

RAG matching has also since been implemented using OpenAI embeddings and Postgres/pgvector, followed by semantic reranking, reciprocal fit evaluation and a relationship-level reasoning step.

## Decision after Round 1

**Decision: continue with Anaphora and the same core use case.**

There was no change of industry or fundamental business problem after presenting Round 1 to teaching staff.

The Round 2 focus became:

- strengthening the Relationship Blueprint as structured product state;
- improving the separation between conversation, extraction and later reasoning;
- implementing RAG-based candidate retrieval;
- moving from one-sided similarity toward reciprocal compatibility reasoning;
- expanding Blueprint enrichment through Discoveries and friend input;
- developing the concept into a deployed, testable end-to-end MVP.

## Status at the Round 2 midpoint

Since Round 1, the MVP has progressed from concept / early prototype into a live product flow that external testers can use.

Major additions include:

- structured `ME` and `IDEAL_PARTNER` Blueprint signals;
- deterministic readiness logic;
- multiple Discoveries;
- friend contribution flows;
- RAG retrieval against a synthetic candidate pool;
- reciprocal matching in both directions;
- relationship-level compatibility reasoning and grounded explanations;
- LangChain-based orchestration with optional LangSmith tracing;
- lightweight tester-session analytics for qualitative user testing.

The remaining work is primarily refinement, testing, compliance/business documentation, and preparation of the final presentation rather than a change in product direction.
