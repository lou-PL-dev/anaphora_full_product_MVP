# Opportunities & Risks — AI for Anaphora

## Opportunities

1. **Scenario-based self-discovery beats a personality test for onboarding.**
   Rather than one "psychometric assessment" score, users move through
   short, visually distinct "Discoveries" — situational choices and
   trade-offs (e.g. "what would you want your partner to do after a bad
   day", forced trade-offs like roots vs. freedom) rather than abstract
   rating scales. This separates personality, values, relationship
   dynamics, lifestyle, and attraction into distinct dimensions instead of
   one blended score — mirroring how established frameworks (e.g. Gottman's
   areas of friendship/intimacy, conflict, values/goals, trust, lifestyle)
   already treat compatibility as multi-dimensional, not a single number.
   Lower onboarding friction than a form, richer signal than free text alone.

2. **Explainable, multi-source matching builds trust where competitors
   don't.** Most incumbents give a black-box score. Anaphora's model
   compares three perspectives per trait — what the user says, what their
   own choices/patterns reveal, and what friends observe — and surfaces
   where they *converge* (strong signal) versus *diverge* (something worth
   exploring), rather than a flat "92% match." This directly answers
   Chleo's "AI isn't transparent" fear and turns explainability into the
   core product experience, not a compliance afterthought.

3. **Friend-input as a defensible, deeper wedge.** No direct competitor
   blends a structured friend perspective into the actual matching signal
   the way Anaphora's "Ask someone who knows you" flow does (Wingman is
   swipe-only vouching, not a mapped-to-the-same-dimensions data source).
   Friends answer through a no-install, no-account mobile webpage and go
   through a lightweight, conversational version of the same discovery —
   small team, high differentiation, and a natural viral/growth loop
   (each user invites 1-3 friends).

4. **Foundation-model APIs remove the need for an in-house ML team.** A
   startup this size can ship a credible AI product using LangChain +
   hosted LLMs + a vector DB, without hiring data scientists — this is the
   core argument for *why AI consulting matters here*: the technical bar
   to compete just dropped.

5. **Multiple monetization angles beyond pay-per-contact** — deeper
   Discoveries, the full Relationship Blueprint, local events, and
   (roadmap) reflective tools like "relationship archaeology" — align with
   the loneliness-focused mission and give room to expand ARPU without
   relying on contact-unlock fees alone.

## Risks

| Risk | Type | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| Cold-start: not enough profiles per city to produce good matches | Operational | High | High | Single-city launch (Paris), synthetic seeding for demo, partner with local events for early density |
| Pay-per-contact unit economics don't cover LLM/embedding + CAC costs | Financial | Medium | High | Model costs explicitly per user (Round 2 ROI doc); consider bundle pricing like Sitch |
| Discovery data (values, attraction patterns, attachment-style-adjacent traits) is personality/behavior-inferred data — GDPR special-category or high-risk-profiling exposure | Regulatory | Medium | High | Legal basis review, DPIA (Round 2), minimize inferred-trait storage, explicit consent flows, avoid diagnostic-sounding language (e.g. never label a user "anxiously attached" — describe tendencies instead, as the product design already intends) |
| EU AI Act: matching/profiling system likely triggers transparency obligations (at minimum) | Regulatory | Medium | Medium | Classify system risk tier early (Round 2 doc), build explainability in from day one — already core to the product design |
| Trust/safety: catfishing, harassment, friend-invite misuse | Ethical/Reputational | Medium | High | Verification step, reporting flow, human review for flagged profiles |
| "Relationship archaeology" (reflecting on past relationships) and friend commentary on past partners touch emotionally sensitive territory | Ethical | Medium | Medium | Frame as optional and reflective, never diagnostic; friend answers about a user's exes are never shown to matches, only feed structured, anonymized dimensions |
| AI match explanations perceived as manipulative or "too accurate" (creepy factor) | Ethical | Low-Medium | Medium | Keep explanations grounded in what the user and friends actually said, not inferred/derived traits beyond what's presented; give users a way to react ("that resonates" / "not quite") rather than presenting conclusions as fact |
