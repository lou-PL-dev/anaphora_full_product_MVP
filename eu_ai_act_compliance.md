# Anaphora — EU AI Act Compliance Documentation

*Last updated 2026-09-03. Written against the actual current implementation
and product copy (`conversation_chain.py`'s system prompt, `Welcome.jsx`,
`Legal.jsx`) rather than a generic template. Not legal advice — have this
reviewed by counsel before any public launch. Regulation (EU) 2024/1689
(the AI Act) applies its obligations in phases by date; this document's
timeline references (§5) should be re-verified against current official
guidance before being relied on operationally, since delegated/implementing
acts continue to be published as the phase-in progresses.*

## 0. Status and scope

Anaphora is a private MVP in active testing (see `gdpr_documentation.md`
§0 for the same framing on the data-protection side). This document
classifies the AI system as it exists **today** — a conversational
matchmaking assistant, structured-data extraction, and a RAG-based
candidate matcher, all built on third-party foundation models accessed via
API (OpenAI). It does not classify any hypothetical future feature.

**Provider/deployer roles**: Anaphora is a **deployer** of OpenAI's
GPT-4o / GPT-4o-mini / text-embedding-3-small models (accessed via API,
no fine-tuning or model weights hosted by Anaphora) and the **provider**
of the Anaphora *application* built on top of them. General-purpose AI
model provider obligations (Title VIIIa / Article 53 and related
provisions) fall on OpenAI, not on Anaphora — Anaphora's own obligations
are those of a deployer/downstream provider of an AI *system*, which is
what this document classifies.

---

## 1. Risk classification — step-by-step reasoning

### 1.1 Is Anaphora a prohibited AI practice (Article 5)?

Walking through each prohibited category in Article 5(1) against what the
system actually does:

| Prohibited practice | Applies to Anaphora? | Reasoning |
|---|---|---|
| (a) Subliminal/manipulative techniques causing significant harm | **No** | The conversation is transparent and user-initiated for a stated purpose (matchmaking); no covert or manipulative technique is used to distort behavior against the user's interest |
| (b) Exploitation of vulnerabilities (age, disability, socio-economic situation) | **No** | General adult audience (18+, self-attested per `Legal.jsx`'s Terms section — not currently age-verified, see §3); no design targets a vulnerable group |
| (c) Social scoring | **No** | Not applicable to this domain |
| (d) Individual crime-risk prediction from profiling alone | **No** | Not applicable |
| (e) Untargeted facial-image scraping for recognition databases | **No** | No facial recognition or image scraping of any kind |
| (f) Emotion inference in workplace/education | **No** | Not a workplace or education context |
| (g) Biometric categorisation to infer sensitive attributes (incl. sexual orientation) | **No — but this is the closest near-miss and deserves explicit reasoning** | Anaphora *does* infer relationship/attraction preferences that are sensitive in nature (see `gdpr_documentation.md` §2), but it does so from **self-reported conversational text the user chooses to share**, not from **biometric data** (facial images, voiceprints, gait, etc.). Article 5(1)(g) is specifically about biometric categorisation; inferring stated preferences from natural-language input is a different legal category (ordinary special-category personal data processing under GDPR Article 9, already addressed in `gdpr_documentation.md`). |
| (h) Real-time remote biometric identification in public spaces (law enforcement) | **No** | Not applicable |

**Conclusion: not a prohibited practice under Article 5.**

### 1.2 Is Anaphora high-risk (Article 6 / Annex III)?

Two routes to high-risk status:

- **Art. 6(1) — safety component of a product under EU harmonisation legislation (Annex I)**: Anaphora is not a safety component of machinery, medical devices, toys, or any other Annex I product category. **Not applicable.**
- **Art. 6(2) — Annex III use-case list**: walking through all eight categories —

| Annex III category | Applies? |
|---|---|
| Biometrics | No |
| Critical infrastructure management | No |
| Education/vocational training (admission, assessment) | No |
| Employment, worker management, self-employment access | No |
| Access to essential private/public services (credit scoring, life/health insurance risk assessment & pricing, public benefit eligibility, emergency dispatch prioritisation) | **No** — dating/matchmaking is a discretionary consumer service, not one of the specifically enumerated "essential services"; it does not gate access to credit, insurance, benefits, or emergency response |
| Law enforcement | No |
| Migration, asylum, border control | No |
| Administration of justice, democratic processes | No |

**Conclusion: not high-risk under Annex III.** Matchmaking/relationship
recommendation is not an enumerated high-risk category, and none of the
underlying mechanisms (conversation, extraction, RAG retrieval,
LLM-based match reasoning) constitute a safety component under Art. 6(1).

### 1.3 Does Anaphora trigger transparency obligations (Article 50)?

Yes, on two independent grounds:

1. **Art. 50(1) — direct interaction with a natural person**: the
   conversational onboarding flow is exactly this. Disclosure is already
   substantially in place: the very first screen a user sees states
   *"AI that listens"* before the "Begin" button (`Welcome.jsx`), the
   system prompt frames the assistant as *"a warm, perceptive AI
   matchmaker"* (`conversation_chain.py`), and the product is branded and
   marketed as an AI matchmaking app throughout — the "obvious from the
   circumstances" bar is comfortably met. **Recommendation**: keep an
   equivalent, unambiguous cue visible on the chat screen itself
   (`Chat.jsx`), not only on the entry screen, so the disclosure holds up
   even for a user who lands mid-flow (e.g. via a shared link) without
   passing through `Welcome.jsx` first.
2. **Art. 50(2)/(4) — AI-generated content**: the Blueprint narrative
   portrait and match explanations shown to users are LLM-generated text.
   `Legal.jsx` already discloses this generally (*"Match suggestions,
   narrative portraits, and explanations are AI-generated..."*). **One
   open item**: the ~50 synthetic candidate profile photos
   (`frontend/public/candidates/`) depict fictional people who don't
   exist — their provenance (real licensed stock photography vs.
   AI-generated faces) isn't documented in the repository
   (`frontend/public/candidates/README.md` only specifies filenames/crop
   spec, not source). **If any are AI-generated**, Article 50(2)'s
   synthetic-image marking obligation plausibly applies, and this should
   be confirmed and, if needed, remediated (source verifiably-licensed
   stock photography instead, or add a machine-readable synthetic-content
   marker) before any wider release.

**Conclusion: Anaphora is classified as Limited Risk under the EU AI Act**
— not prohibited, not high-risk, but subject to the Article 50 transparency
obligations discussed above and detailed in §2.

### 1.4 General-purpose AI model considerations

Anaphora does not train, fine-tune, or distribute a general-purpose AI
model — it calls OpenAI's hosted models via API. GPAI provider obligations
(systemic-risk assessment, technical documentation of the model itself,
copyright-policy summaries, etc.) sit with OpenAI, not Anaphora. Anaphora's
only corresponding duty is ordinary supply-chain diligence — confirming
OpenAI's own AI Act compliance posture as a GPAI provider — which is a
lighter-weight check than being a GPAI provider itself.

---

## 2. Mandatory requirements summary (Limited Risk — Article 50)

Because Anaphora classifies as **Limited Risk**, the full high-risk regime
(Articles 8-15: risk management system, data governance, Annex IV
technical documentation, automatic logging, human oversight, accuracy/
robustness/cybersecurity requirements, third-party or internal conformity
assessment, CE marking, EU database registration) **does not legally
apply**. What *does* apply:

| Requirement | Legal basis | Status |
|---|---|---|
| Disclose that users are interacting with an AI system | Art. 50(1) | **Met** — see §1.3. Recommend reinforcing on the chat screen itself, not just the entry screen. |
| Mark AI-generated content appropriately | Art. 50(2)/(4) | **Substantially met for text** (Blueprint narratives, match explanations — disclosed in `Legal.jsx`). **Open item**: confirm candidate photo provenance (see §1.3). |
| General AI literacy for staff/operators (Art. 4) | Art. 4 | Applies to the developer/operator running Anaphora. At single-founder MVP scale this is informally satisfied by the developer's own direct involvement in building the system; **formalize once the team grows** (a short internal AI-literacy note covering what the LLM can/cannot be trusted to do, and this document's own risk classification, is sufficient at this stage). |
| Registration in the EU high-risk AI database | Art. 71 | **Not applicable** — only required for high-risk systems |
| Conformity assessment / CE marking | Arts. 8, 43 | **Not legally required** at Limited Risk. A voluntary self-assessment is still provided in §3, both to satisfy this assignment's requirement to demonstrate the methodology and because it's useful preparation if a future feature ever changed the classification (see §5). |

---

## 3. Conformity Assessment Summary (voluntary)

*Framing note: this section is not a legal obligation for a Limited-Risk
system — it's included because (a) the assignment requires it and (b) it's
genuinely useful practice for a team that may add features later. It's
structured loosely on the Annex VI "internal control" self-assessment
procedure that would apply if Anaphora were ever high-risk, scaled down
to what's proportionate for a Limited-Risk consumer app today.*

**Intended purpose**: an AI-assisted conversational matchmaking system
that (1) extracts a structured "Relationship Blueprint" from a guided
conversation and short questionnaires, (2) computes a deterministic
readiness score independent of any single LLM call, and (3) retrieves and
explains candidate introductions from a synthetic pool via reciprocal
semantic matching and grounded LLM reasoning. Intended users are adults
seeking a serious relationship; not intended for anyone under 18
(self-attested, not currently age-verified — disclosed in `Legal.jsx`'s
Terms section, and related to the pseudonymous-identity limitations
discussed in `gdpr_documentation.md` §6).

**Risk-mitigation measures already in place**:
- Readiness gating is **deterministic Python logic**
  (`anaphora_backend/app/readiness.py`), not an LLM judgment — the system
  won't offer to show matches based on a model's say-so alone.
- The final match verdict passes through **two independent gates**: an
  LLM's qualitative judgment (`relationship_reasoning_chain.py`) *and* a
  hard-coded deterministic score/evidence threshold
  (`matching_chain_v5.py`'s `strong_fit_allowed` check) — a persuasive but
  ungrounded LLM explanation cannot alone upgrade a weak match to a
  confident one.
- Prompts explicitly instruct the model never to invent evidence and to
  treat absence of evidence as uncertainty, not incompatibility (see the
  system prompts in `matching_chain.py` and `relationship_reasoning_chain.py`).
- A known scoring-quality bug (category-gap and category-label matching
  issues that suppressed compatibility evidence) was identified and fixed
  earlier in this project's development, with regression tests added
  (`test_matching.py`) — evidence of an active, working feedback loop
  between observed AI behavior and system correction, which is itself
  good AI-governance practice.
- Sensitive-inference handling is disclosed to users in plain language
  before they engage (`Legal.jsx`, `Welcome.jsx`) — see §1.3.

**Known residual risks** (cross-referenced with `gdpr_documentation.md`
§5 and §8, since data risk and AI-system risk overlap heavily for this
product):
- LLM outputs (narrative portraits, match explanations, conversational
  replies) can still be wrong, oddly phrased, or occasionally reflect
  model idiosyncrasy despite grounding instructions — `Legal.jsx`'s Terms
  section already discloses this to users ("may be imperfect or
  occasionally wrong").
- No automated evaluation/monitoring pipeline currently scores match
  quality or conversational quality in production beyond the lightweight
  tester-event analytics described in `gdpr_documentation.md` §1 —
  quality is currently assessed by manual review of tester sessions via
  the admin panel. Worth formalizing before a wider pilot (see §5).
- Candidate photo provenance is unconfirmed (§1.3).

**Self-declared conclusion**: on the basis of the reasoning in §1, Anaphora
is assessed as Limited Risk. No CE marking or formal declaration of
conformity is legally required. This self-assessment should be revisited
whenever a materially new feature is added — see §5 for specific triggers.

---

## 4. Technical Documentation Outline (voluntary — modeled on Annex IV)

*As with §3, a full Annex IV technical file is not legally required at
Limited Risk. This outline is provided so the underlying documentation
already exists in a structured form — most of it is simply a pointer to
material this project already has — and so expanding it later (if the
classification ever changes, see §5) is a matter of depth, not a
from-scratch exercise.*

1. **General description of the system**
   1.1 Intended purpose and users — see §3
   1.2 System architecture — `mvp_documentation.md` §3 (Frontend/Backend/Database/AI orchestration)
   1.3 Interaction with hardware/software, deployment context — Render + Netlify, see `README.md`
2. **Design specifications**
   2.1 Development process and methodology — `mvp_documentation.md` §4 (Core AI flows)
   2.2 Model(s) used and their role — GPT-4o (conversation), GPT-4o-mini (extraction, Discovery insight, match reasoning), text-embedding-3-small (RAG retrieval) — see `README.md`'s "Tech stack"
   2.3 Validation and testing approach — `mvp_documentation.md` §9 (Testing and observability); this project's automated test suite (`anaphora_backend/test_*.py`)
3. **Data**
   3.1 Training/fine-tuning data — **N/A**, no model training or fine-tuning occurs; all models are used as-is via API
   3.2 Data used at inference time — conversation transcripts, structured Blueprint signals, synthetic candidate pool — see `gdpr_documentation.md` §1 for the full data inventory
   3.3 Data governance — `gdpr_documentation.md` in full
4. **Monitoring, functioning, and control**
   4.1 Human oversight measures — deterministic gates described in §3; manual admin review of tester sessions
   4.2 Accuracy metrics — not yet formalized as an automated metric (flagged as a gap in §3); readiness/match-return rates are currently the closest proxy, visible via the admin panel
   4.3 Known limitations — `mvp_documentation.md` §10 (Current limitations versus production)
5. **Risk management**
   5.1 Risk classification reasoning — §1 of this document
   5.2 Identified risks and mitigations — §3 of this document, `gdpr_documentation.md` §5 (DPIA) and §8 (remediation roadmap)
6. **Change log**
   6.1 To be maintained going forward — recommend a running log of material changes to the conversation prompts, scoring logic, or candidate pool composition, since any of these could shift the risk profile described in §1

---

## 5. Re-classification triggers and monitoring

This classification (§1) holds for Anaphora **as it exists today**. It
should be explicitly re-assessed, not assumed to still hold, if any of the
following happen:

- Anaphora ever adds **age or identity verification using biometric
  data** (e.g. facial age estimation) — this would introduce a biometric
  processing dimension not present today and needs fresh Article 5/Annex
  III analysis.
- Anaphora ever expands into **any Annex III-adjacent domain** — e.g. a
  future "relationship coaching for employer wellness programs" pivot
  would touch the employment category; a credit-linked premium-tier
  eligibility check would touch essential services. Neither is planned,
  but the trigger is worth naming explicitly.
- The **candidate photo provenance question** (§1.3) resolves to
  AI-generated — implement the Art. 50(2) marking remediation described
  there.
- The system starts generating **synthetic audio/video** (e.g. an AI
  "video intro" feature) — this would engage Art. 50(2)'s deepfake-marking
  obligation more directly than the current static-image/text case.

**On timeline**: at the time of writing, the AI Act's prohibitions
(Art. 5) and its transparency obligations (Art. 50, relevant here) are
understood to already be in force, with the high-risk regime phasing in
on a later schedule that does not affect this Limited-Risk classification
either way. Confirm current applicability dates against the official
Regulation and any published delegated/implementing acts before treating
this section as current, since the phase-in schedule continues to be
refined.
