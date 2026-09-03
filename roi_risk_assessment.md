# Anaphora — ROI and Risk Assessment

*Last updated 2026-09-03. The cost side of this document builds directly
on the measured/labeled-assumption methodology already established in
`product_document/cost_timeline_estimate.md` and
`product_document/cost_estimate/cost_model.py` — real per-call LLM costs
computed from the actual shipped prompts, not re-guessed here. The
revenue side uses figures the founder explicitly approved for this
document (pricing, growth trajectory, funding, conversion rate) since
none of that is committed anywhere else in the repo — `use_case_definition.md`
§6 explicitly places "payments and subscription billing" out of scope for
the current MVP stage, and the PRD's monetisation section (§27) defines
the three subscription tiers' *features* but states "exact pricing is
outside the scope of this PRD." Every founder-approved figure is labeled
as such below, exactly the way the existing cost model labels its own
guesses — change any of them and the numbers that follow should be
recomputed, not assumed to still hold. **Currency note**: pricing is
quoted in EUR (the approved figures); infrastructure costs in the existing
cost model are in USD. Given how small the absolute infra figures are
relative to team cost, this document treats $1 ≈ €1 for simplicity — an
explicitly immaterial rounding choice, not a business assumption.*

---

## 1. Upfront costs

| Item | Amount | Basis |
|---|---|---|
| Illustrative pre-seed raise | **€500,000** | Founder-approved figure for this document. Standard pre-seed range for a 5-8 person team (`use_case_definition.md` §2's stated team size); funds the runway computed in §6 below. |
| Candidate pool seeding (one-time) | **€0.11** | Measured, not estimated — `cost_timeline_estimate.md`'s "One-time cost: seeding the candidate pool," 50 synthetic candidates at $0.0022/candidate |
| **Total upfront** | **≈€500,000** | The seeding cost is immaterial (11 cents) next to the raise — included for completeness, not because it moves the total |

## 2. Ongoing costs

Two very different orders of magnitude, worth stating plainly up front:
**team cost dominates infrastructure cost by roughly 700:1** at this
stage. This project's own cost modeling work has focused (correctly, for
an engineering deliverable) on the infra/LLM side — but for an honest ROI
picture, team burn has to be the headline ongoing cost, not a footnote.

| Item | Monthly amount | Basis |
|---|---|---|
| Team burn (5-8 people, blended pre-seed compensation) | **≈€30,000/month** | Founder-approved raise (€500K) implies a working runway assumption; €30K/month gives ≈16-17 months runway on the pre-seed alone — consistent with a typical pre-seed timeline to a seed round, not stretching an unrealistic 3 years off one raise (see §6's break-even note for why this matters) |
| Hosting (paid tier — backend + Postgres + frontend) | **$33.00** | Measured in `cost_timeline_estimate.md` — Render Starter ($7) + Render Postgres Basic-256mb ($6) + Netlify Pro ($20), needed to avoid cold-starts and the free Postgres tier's 30-day expiry once beyond a private pilot |
| Analytics (Plausible Starter) | **$9.00** | Measured in `cost_timeline_estimate.md` — EU-hosted, no-cookie-banner choice consistent with the product's own privacy positioning |
| LLM cost per new user | **$0.01755/signup** | Measured, not estimated — `cost_timeline_estimate.md`'s per-user-journey figure (one conversation + Blueprint canonicalization + one Discovery + one `/matches` call), computed from the actual system prompts shipped in `anaphora_backend`. This prices each member's *first* journey only — it does not yet include the extra canonicalization cost a returning member's later Discoveries, friend contributions, or corrections add (each re-canonicalizes their full evidence history); see `cost_timeline_estimate.md`'s "Key finding" for why that's a real cost driver to re-measure once there's usage data, not a rounding error |
| **Fixed monthly floor** | **≈€30,042** | Team burn is ~99.86% of this — infrastructure is not the ongoing-cost story at this scale |

---

## 3. Quantified business value

**Pricing** (founder-approved, filling in the PRD §27 tiers that were
deliberately left unpriced):

| Tier | Price | What it includes (PRD §27) |
|---|---|---|
| FREE | €0 | Initial conversation, basic Blueprint, limited Discoveries — no matches |
| LIGHT | €14.99/mo | Expanded conversation/Discoveries, up to 3 friend invitations, 1 curated match/month |
| PREMIUM | €29.99/mo | Full Discovery library, unlimited friend invitations, 2 curated matches/month |

**Growth trajectory** (founder-approved — conservative, single-city
pace, consistent with the cold-start mitigation already in the Round 1
risk table): **500 registered users by month 12, 5,000 by month 36**,
modeled as linear growth between anchor points (0→500 over months 1-12,
500→5,000 over months 13-36) for simplicity — a real adoption curve would
be S-shaped, but a straight line is the honest default absent any real
signup data to fit a curve to.

**Conversion**: **6.5%** free-to-paid (midpoint of the founder-approved
5-8% range), split **70% LIGHT / 30% PREMIUM** among paying users (this
70/30 split is *not* one of the founder-approved figures — it's a
standard freemium skew-to-the-cheaper-tier assumption, flagged here so it
can be revisited). Blended ARPU per paying user:
`0.70 × €14.99 + 0.30 × €29.99 = €19.49/month`.

| Period | Avg. registered users | Avg. paying users (6.5%) | Cumulative revenue |
|---|---|---|---|
| Months 1-12 | 250 (ramping 0→500) | ≈16.3 | 16.3 × €19.49 × 12 ≈ **€3,801** |
| Months 13-36 | 2,750 (ramping 500→5,000) | ≈178.8 | 178.8 × €19.49 × 24 ≈ **€83,612** |
| **Cumulative through month 36** | | | **≈€87,413** |

This is intentionally modest — it's the honest output of a *conservative,
single-city, freemium* growth model, not a discounted-cash-flow
projection dressed up to look better. See §4 for what this means for ROI,
and §6 for the strategic implication.

---

## 4. ROI: 12 and 36 months

`ROI = (Net Benefit / Total Cost) × 100`, where Net Benefit = cumulative
revenue − Total Cost, and Total Cost = upfront cost + cumulative ongoing
cost over the period.

| | 12 months | 36 months |
|---|---|---|
| Upfront cost | €500,000 | €500,000 |
| Cumulative team burn | €30,000 × 12 = €360,000 | €30,000 × 36 = €1,080,000 |
| Cumulative infra/LLM cost | ≈€513 | ≈€1,600 |
| **Total cost** | **€860,513** | **€1,581,600** |
| Cumulative revenue | €3,801 | €87,413 |
| **Net benefit** | **−€856,712** | **−€1,494,187** |
| **ROI** | **≈ −99.6%** | **≈ −94.5%** |

**This is deeply negative at both horizons, and that's the honest,
expected shape for a pre-revenue consumer subscription product at this
growth pace — not a modeling error.** A pre-seed-stage company isn't
funded on a positive 12- or 36-month ROI; it's funded on trajectory and
thesis. The cumulative Net Benefit necessarily looks *more* negative at
36 months than at 12 (more months of team burn accumulate either way) —
the number worth watching instead is the **monthly** burn rate: average
monthly net cash flow narrows from ≈−€29,700/month in year 1 to
≈−€26,600/month across months 13-36, as the compounding user base's
revenue increasingly offsets the flat €30,042/month cost floor. That's a
real, if modest, improving trend — and §6 makes explicit what would need
to change for that trend to actually reach profitability, which is the
real question a seed-stage investor (or this assignment) should be
asking, not the cumulative total in isolation.

---

## 5. Assumptions table

| Assumption | Value | Status |
|---|---|---|
| Pre-seed raise | €500,000 | Founder-approved for this document |
| LIGHT price | €14.99/mo | Founder-approved |
| PREMIUM price | €29.99/mo | Founder-approved |
| Growth trajectory | 500 users @ month 12, 5,000 @ month 36 | Founder-approved |
| Free-to-paid conversion | 6.5% (midpoint of approved 5-8%) | Founder-approved range, midpoint chosen for a single point estimate |
| Paid-tier split | 70% LIGHT / 30% PREMIUM | **Not founder-approved** — a standard freemium-skew default, flagged for revisiting |
| Team burn | €30,000/month | Derived from the €500K raise assuming ≈16-17mo pre-seed runway, not independently approved — see §6 |
| Growth curve shape | Linear between anchor points | Simplification — no real signup data exists yet to fit a curve to (same honesty principle as `cost_timeline_estimate.md`'s labeled guesses) |
| USD→EUR | 1:1 | Rounding simplification — infra costs are immaterial next to team cost either way |
| Per-user LLM cost | $0.01755/signup | **Measured**, not assumed — from the actual shipped prompts; first-journey cost only, see caveat in §2 |
| Fixed monthly hosting+analytics | $42/month | **Measured** — see `cost_timeline_estimate.md` |

---

## 6. Break-even note

**Break-even is not reached within the 36-month horizon at this growth
trajectory — and the €500K pre-seed raise alone doesn't cover 36 months
of operation in the first place.** Two separate findings worth stating
plainly rather than glossing over:

1. **Runway**: €500,000 ÷ €30,000/month ≈ **16.7 months**. The 36-month
   figures in §4 necessarily assume a follow-on raise happens somewhere
   around month 15-17 — this document doesn't model that raise's size or
   terms (out of scope for a cost/revenue analysis; it belongs in
   `strategic_plan.md`'s funding milestones), but it's a real dependency
   the 36-month column rests on, not something this analysis can paper
   over.
2. **Operational break-even** (MRR covering the €30,042/month fixed
   floor, independent of the sunk upfront raise) requires:
   `€30,042 ÷ (6.5% × €19.49 blended ARPU) ≈ 23,714 registered users`.
   At the approved months-13-36 growth rate (≈187.5 net new users/month),
   reaching 23,714 users from the month-36 figure of 5,000 would take
   roughly **another 100 months** at the *same linear pace* — i.e., well
   over a decade, which is not a credible standalone plan.

**The strategic implication, not just the arithmetic**: the conservative,
single-city trajectory approved for this document is appropriate for
*validating the product* (which is exactly what the current MVP and
tester round are doing), but it is not, by itself, a path to
profitability. Reaching break-even in a reasonable timeframe needs at
least one of: faster growth (multi-city expansion, funded by a seed
round), materially better unit economics (higher conversion or ARPU than
this document's conservative assumptions), or a leaner cost structure
once past the validation phase. This tension — and which lever to pull
first — is exactly what `strategic_plan.md` (next deliverable) should
resolve.

---

## 7. Risk matrix

Eight risks spanning all four required categories — the first two rows
(cold-start, and the financial/unit-economics risk folded into the
operational row below) were already identified in Round 1's
`research/opportunities_risks.md`; the technical and several regulatory
rows are new, surfaced by this project's own development and the
compliance documentation already produced this round.

| # | Risk | Category | Likelihood (1-5) | Impact (1-5) | Mitigation |
|---|---|---|---|---|---|
| 1 | Cold-start: not enough candidate density in a single city to produce good matches | Operational | 4 | 5 | Single-city launch (Paris), synthetic seeding for the pilot, partner with local events for early density (Round 1 finding, still the current mitigation) |
| 2 | Free-tier infrastructure fragility (Render Postgres expires 30 days after creation; backend cold-starts after 15min idle; Netlify's ~300 deploy-credits/month can exhaust in days at active-development pace) | Operational | 4 | 3 | Upgrade to the paid tier (~€33/mo, already costed in §2) before any real pilot beyond private testing; this was nearly mistaken for actual data loss during this project's own testing round, underscoring the risk is real, not theoretical |
| 3 | GDPR special-category data exposure — inferring attraction/relationship preferences is likely Article 9 processing, and the current consent mechanism (starting a conversation) is legally thinner than a distinct opt-in | Regulatory | 3 | 5 | DPIA completed (`gdpr_documentation.md` §5); explicit consent checkpoint recommended before wider pilot (`gdpr_documentation.md` §8) |
| 4 | EU AI Act Article 50 transparency gaps — AI-disclosure not reinforced on the chat screen itself, and synthetic candidate photo provenance is undocumented | Regulatory | 2 | 3 | Risk classification completed (`eu_ai_act_compliance.md` §1); both gaps tracked with concrete remediation in §2/§5 of that document |
| 5 | Matching-quality degradation — reciprocal scoring logic can silently suppress genuine compatibility evidence (a real bug of exactly this kind was found and fixed during this project's own tester round) | Technical | 3 | 4 | Regression tests added (`test_matching.py`) covering the specific failure modes found; admin-panel tester analytics provide an ongoing early-warning signal, though no automated match-quality metric exists yet (tracked as a gap) |
| 6 | Single third-party LLM dependency — every core AI function (conversation, extraction, embeddings, match reasoning) runs through one provider (OpenAI); an outage, pricing change, or policy change directly disables the product | Technical | 2 | 5 | LLM client construction is already centralized (`app/llm.py`) rather than scattered across call sites, which is the actual prerequisite for ever adding a fallback provider — no fallback exists yet, tracked as a forward-looking mitigation, not a current one |
| 7 | Trust & safety — catfishing, harassment, or friend-invite misuse once real (non-synthetic) users are matched with each other | Ethical | 3 | 5 | Not yet built: identity verification step, in-app reporting flow, human review queue for flagged profiles (Round 1 finding, still open — explicitly out of scope for the current MVP per `use_case_definition.md` §6) |
| 8 | AI-inferred relationship patterns and reflective features (e.g. "relationship archaeology") touch emotionally sensitive territory — risk of feeling surveilled, diagnosed, or manipulated by an AI's confident-sounding explanation | Ethical | 3 | 3 | Grounded-evidence-only prompting (explicit "never invent evidence" instructions in every relevant system prompt); explanations frame observations as reflective, not diagnostic; user always retains the decision to engage, per `use_case_definition.md` §3's "the AI does not autonomously make consequential decisions for users" |

**Reading the matrix**: the two highest-severity, non-trivial-likelihood
risks are #1 (cold-start) and #3 (GDPR special-category consent) — both
already have concrete, partially-implemented mitigations rather than
being purely theoretical. #6 (LLM dependency) is high-impact but
currently low-likelihood and explicitly deferred as a forward-looking
item, which is a reasonable prioritization call for a pre-pilot MVP, not
an oversight.
