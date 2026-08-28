# Anaphora — Round 1 Dashboard (FastAPI + vanilla JS)

Built from the Claude Design mockup as a
real, runnable app — the mockup's own README notes it's a preview-only
prototype (`x-dc`/`support.js` runtime), so this reimplements the same
layout, palette, and behavior in plain HTML/CSS/JS + FastAPI.

## Run it
```
pip install -r requirements.txt
cp .env.example .env   # then paste your real OPENAI_API_KEY
uvicorn dashboard_api:app --reload
```
Open http://localhost:8000

## Files
- `market_data.py` — sourced market figures + TAM/SAM/SOM as parameterized
  functions (sliders drive `pct_single`, `pct_pays`, `capture_y3`)
- `product_data.py` — fixed/seeded simulated product data (funnel, score
  model), matching the design's exact scenario
- `dashboard_api.py` — FastAPI backend. All chart data comes from live
  endpoints, nothing is hardcoded twice. `/api/ask` tries a local
  rule-based answer bank first (instant, can't misstate a sourced figure),
  falling back to OpenAI (grounded in the same live data) for anything else
- `static/` — frontend: fetches from the API, renders KPI cards, the
  TAM/SAM/SOM bars + sliders, incumbent benchmark, SVG trend chart, growth
  comparison, product funnel, and score-distribution chart

## Verified working (this session)
KPIs, TAM/SAM/SOM recompute correctly when sliders change (defaults:
882 → 2,646 users; at 50%/30%/8%: 2,520 → 20,160), local `/api/ask` bank,
and both `/` and `/static/app.js` serve correctly.

**Not tested here:** the OpenAI fallback — this sandbox can't reach
`api.openai.com`. Test that path locally once your real key is in `.env`.