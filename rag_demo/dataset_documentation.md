# Anaphora — synthetic test-dataset documentation

`rag_demo/` generates synthetic Blueprint-shaped personas to test Anaphora's
retrieval and extraction logic against, without using real users' data and
without inventing correlations that don't exist in real people. This
mirrors the discipline applied to the LangSmith custom-dataset lab earlier
in the bootcamp (structured schema, explicit per-field sourcing, documented
generation method) — same standard, applied to dating-profile data instead
of a coaching-eval set.

Two generators produce the same output shape, so anything downstream
(`retrieve_similar`, `build_index`) works on either pool interchangeably:

| | `profiles.py` (baseline) | `generate_personas.py` (upgrade) |
|---|---|---|
| Trait sampling | uniform random, independent per category | drawn from real trait co-occurrence structure |
| Narrative | templated string, no LLM | LLM-written, style-seeded |
| Signal extraction | none — signals ARE the sample | run through `anaphora_backend`'s real extraction chain |
| Needs an API key? | no | yes (LLM narrative + extraction) |

## Fields

Every persona is `{id, narrative, signals[]}`. Each signal is:

| field | type | notes |
|---|---|---|
| `perspective` | `"ME"` \| `"IDEAL_PARTNER"` | matches `anaphora_backend/app/models.py::BlueprintSignal.perspective` |
| `category` | string | `personality`/`lifestyle`/`relationship_dynamic`/`attraction`/`values`/`dealbreakers` for IDEAL_PARTNER; `personality`/`lifestyle`/`relationship_style`/`values` for ME |
| `label` | string | short human-readable trait description |
| `strength` | `"hard_requirement"` \| `"strong_preference"` \| `"preference"` \| `"unknown"` | matches `anaphora_backend/app/schemas.py::Strength` |
| `evidence_text` | string \| null | short supporting quote from the narrative, when extracted (baseline generator leaves this null) |

## How each part is generated

**1. Trait profile** (`trait_distributions.py`) — a Big Five profile (5
traits × low/medium/high) is drawn from a correlated distribution (Cholesky
decomposition of a documented approximate inter-factor correlation
structure, not independent per-trait sampling), and an attachment style
(secure/anxious/avoidant/fearful-avoidant) is derived from the SAME draw via
the standard ECR anxiety/avoidance quadrant classification, correlated with
neuroticism/agreeableness/extraversion per the cited literature. This trait
profile describes the **ideal partner** the persona is going to say they
want — matching Anaphora's actual product (a user describes who they want,
not themselves).

**2. Narrative** (`generate_personas.py::generate_narrative_via_llm`) — an
LLM is prompted to write that trait profile as a natural first-person
message, with four originally-written example sentences included in the
prompt purely as REGISTER references (casual, specific, a little
imperfect) — the model is explicitly told not to reuse their wording or
topics. See "Style seeding" below for why these are original text, not
real dataset excerpts.

**3. Extraction** (`generate_personas.py::generate_persona`) — the
narrative is wrapped as a two-turn conversation (the same opening prompt
`anaphora_backend` uses, plus the narrative as the user's reply) and run
through `anaphora_backend/app/chains/extraction_chain.py::extract_blueprint`
directly — the exact code a real conversation's Blueprint goes through, not
a reimplementation of it.

## Exact sourcing for the trait distributions

Full citations and the honest limitations of each are in
`trait_distributions.py`'s module docstring — summarized here:

- **Dataset existence/scale**: Open-Source Psychometrics Project raw data
  index, https://openpsychometrics.org/_rawdata/ (its `IPIP-FFM-data-8Nov2018.zip`,
  1,015,342 respondents, and `ECR-data-1March2018.zip`, 51,492 respondents).
  Confirmed via a third-party mirror of the same index
  (https://github.com/haghish/openpsychometrics) — openpsychometrics.org
  itself was not reachable from the environment this was built in.
  **The raw CSVs were never downloaded or processed** — no individual
  response row from either dataset is stored or reproduced anywhere in this
  repo.
- **Big Five correlation structure**: van der Linden, D., te Nijenhuis, J.,
  & Bakker, A. B. (2010). *The General Factor of Personality: A
  meta-analysis of Big Five intercorrelations and a criterion-related
  validity study.* Journal of Research in Personality, 44(3), 315-327.
  (K=212, N=144,117 — establishes that the Big Five are not orthogonal.)
  The specific correlation values in `BIG_FIVE_CORRELATIONS` encode the
  sign and rough relative magnitude consistently reported across Big Five
  literature, not an exact reproduction of this paper's own matrix.
- **Attachment style classification method**: Bartholomew, K., & Horowitz,
  L. M. (1991). *Attachment styles among young adults: A test of a
  four-category model.* Journal of Personality and Social Psychology,
  61(2), 226-244 (the anxiety × avoidance quadrant model used here).
- **Attachment style prevalence (calibration reference)**: Mickelson, K.
  D., Kessler, R. C., & Shaver, P. R. (1997). *Adult attachment in a
  nationally representative sample.* Journal of Personality and Social
  Psychology, 73(5), 1092-1106 — 59% secure / 25% avoidant / 11% anxious.
  The quadrant cutpoint in `trait_distributions.py` is calibrated so the
  SECURE share lands near 59% as a plausibility check, not an exact target
  (that study used a different, 3-category classification method).

Access date for all of the above: **2026-08-30**.

## Style seeding — and why it isn't real dataset text

`generate_personas.py::STYLE_SEED_EXAMPLES` holds four short example
sentences used only to nudge the LLM's tone away from generic, "obviously
AI-written" phrasing. **These four sentences were written for this repo**,
not sourced from OkCupid, PersonalityCafe, or anywhere else — the original
strategy called for seeding style from real free-text excerpts, but this
build had no access to the actual OkCupid Kaggle dataset's content, and
storing real people's text (even a few sentences, even for tone only) would
undercut the exact privacy principle that approach was meant to preserve.
The prompt tells the model explicitly to match register, not to reuse the
examples' wording or content — swapping in real excerpts later (with proper
handling — never persisted verbatim in generated output) would be a
drop-in change to `STYLE_SEED_EXAMPLES` if the real dataset becomes
available.

## Sample size

No fixed pool has been committed to the repo — `generate_personas.py` is a
generator, run with `python generate_personas.py -n <count>`. The original
strategy brief's target scale (matching the datasets it's grounded in) is
in the hundreds to low thousands for a meaningful test pool; this was not
run at that scale here because doing so requires a real `OPENAI_API_KEY`
(this environment had none — see Limitations).

## Known limitations

- **Fully synthetic.** No real user or real dater's data appears anywhere
  in this pipeline. Trait *distributions* are grounded in real published
  psychometric findings; the individual personas themselves are invented.
- **General population, not a dating-app population.** Both source
  datasets are open online personality tests, not sampled from people
  actively dating — the OkCupid dataset considered and rejected in the
  original strategy (see the brief) would have been closer to a real
  dating-app population but had no equivalent depth on describing an ideal
  partner, only self-description.
- **Correlation structure is literature-typical, not dataset-specific.**
  `BIG_FIVE_CORRELATIONS` and the attachment-prevalence calibration reflect
  values consistently reported across the broader psychometric literature
  on these instruments, not a fresh computation from the raw
  openpsychometrics CSVs — this environment could not reach
  openpsychometrics.org to download them. If that access exists elsewhere,
  swapping in dataset-specific computed statistics would only require
  replacing the constants in `trait_distributions.py`; the sampling
  machinery around them (Cholesky-correlated draw, quadrant classification)
  is unchanged either way.
- **ECR sample-size discrepancy.** The strategy brief cites "41,773
  responses" for the ECR dataset; the mirror used to confirm the dataset's
  existence reports 51,492 rows in the raw file. Plausibly the former is a
  complete-responses-only count after the kind of filtering
  openpsychometrics' own codebooks typically describe, but this could not
  be verified without the actual CSV. Documented rather than silently
  reconciled.
- **Attachment prevalence calibration reference uses a different category
  scheme.** Mickelson et al. (1997)'s 59/25/11 split is 3-category
  (Hazan & Shaver forced-choice); this module classifies into 4 categories
  (the ECR/Bartholomew–Horowitz tradition). The two aren't directly
  comparable — see `trait_distributions.py` for the full caveat.
- **Narrative quality depends on a real LLM call.** `offline_narrative()`
  exists purely so the rest of the pipeline (and every test in
  `test_generation.py` except the one explicitly marked end-to-end) can run
  without an API key; it is a visibly templated stand-in, not a claim about
  what real generated output reads like.
- **No changes to `anaphora_backend`.** This is a `rag_demo`-only addition,
  per the brief's own scope — it imports `extract_blueprint` from the
  backend rather than duplicating or modifying it.
