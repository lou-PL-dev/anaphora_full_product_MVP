# Dashboard Documentation — Anaphora Market & Product Dashboard

## What it is
A custom FastAPI + HTML/CSS/JS dashboard (used as the agreed alternative
to PowerBI — confirm this substitution with teaching staff if not already
discussed). It has two views, switchable via the tab bar: **Market
opportunity** and **Product metrics**, plus a **"Ask the data"** bar that
answers questions about the numbers shown, grounded in the same data the
charts render from (local rule-based answers for common questions,
OpenAI fallback for anything else).

Live at `http://localhost:8000` once running — see `dashboard/README.md`
for setup.

## How to navigate
- **Tabs** (top right): "Market opportunity", "Product metrics", "Both"
- **Ask bar**: type a question or click one of the suggested chips
  (e.g. "How did you arrive at the SOM?") for an instant, sourced answer
- **TAM/SAM/SOM sliders**: drag to stress-test the bottom-up SOM
  calculation live — every number on the page recomputes from the same
  backend formulas, nothing is precomputed or hardcoded per slider position

## Metrics — rationale and sources

### Market opportunity view

| # | Metric | Why it's here | Source |
|---|---|---|---|
| 1 | **TAM / SAM / SOM** | Establishes the size of the opportunity top-down (TAM/SAM) and the realistic, defensible bottom-up capture (SOM) for a Paris-first launch — the number a CEO/investor asks for first | MarketDataForecast (TAM), Mordor Intelligence (paying-tier share for SAM), INSEE-style population assumptions for SOM (see `market_data.py` for exact constants) |
| 2 | **Who we're competing for** (incumbent MAU vs. revenue YoY) | Shows scale and momentum have diverged — Hinge is a third of Tinder's size but growing +36% while Tinder shrinks -5.2% — the strategic opening for a new entrant | Business of Apps, Match Group and Bumble Inc. quarterly filings/estimates |
| 3 | **Market growth trend** | Shows the category itself is growing (7.53% CAGR), not just individual apps rising and falling — de-risks the "is this a shrinking market" question | MarketDataForecast, modeled at the sourced CAGR between the 2025/2026/2034 anchor points |
| 4 | **New entrants vs. incumbents** | The single strongest chart for the pitch: PURE grew +95% on a no-swipe design in the same period all three incumbents declined double digits — evidence the swipe model, not the category, is failing | Useluminix, Dating App Market Share & Size 2026 (Q1-Q3 2025, one source for all four data points so they're directly comparable) |
| 5 | **"Why now" stat cards** (single households, loneliness) | Grounds the business case in a demand driver beyond "dating app market growing" — the social-infrastructure story that differentiates Anaphora's positioning | Eurostat household composition statistics; OECD Social Connections and Loneliness report |

### Product metrics view

| # | Metric | Why it's here | Source |
|---|---|---|---|
| 6 | **Onboarding → paid conversion funnel** | Shows where a simulated cohort would drop off, with the paywall step flagged as the constraint worth optimizing first | Simulated/seeded (500 signups) — Anaphora is pre-seed with no real users yet; clearly labeled as such on the dashboard |
| 7 | **Friend-input compatibility lift** | Visualizes Anaphora's core hypothesis — that a friend's perspective, combined with self-report, produces a tighter, higher-quality compatibility signal — as a testable claim, not an unfounded promise | Simulated model (mean 62→71, labeled as a hypothesis to validate in the Paris pilot cohort, not a measured result) |

Two metrics are simulated by necessity (pre-seed, no live users) and are
explicitly labeled as such in the UI — every market-side metric (1-5) is
sourced from public, cited data.

## Screenshots
Place two screenshots in `dashboard/screenshots/`:
- `dashboard/screenshots/market_opportunity.png` — Market opportunity tab
- `dashboard/screenshots/product_metrics.png` — Product metrics tab

Market opportunity view:
![Market opportunity view](screenshots/market_opportunity.png)

Product metrics view:
![Product metrics view](screenshots/product_metrics.png)

## Known limitations vs. a production dashboard
- Product metrics are simulated, not live — clearly flagged in-app, but
  worth restating verbally in the presentation so it isn't mistaken for
  real traction data
- SOM assumptions (% single, % already paying, capture rate) are
  reasoned estimates rather than sourced from a France-specific survey;
  the sliders make this explicit and let the audience stress-test it live
  rather than hiding it behind a single static number
- The "Ask the data" OpenAI fallback is only as good as the live computed
  context it's given — it cannot answer questions about data the
  dashboard doesn't track (e.g. it has no CAC or churn data yet, since
  none exists pre-launch)
