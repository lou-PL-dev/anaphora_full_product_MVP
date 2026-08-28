# Anaphora — Round 1 Dashboard

## Run it
```
pip install streamlit plotly pandas numpy
streamlit run dashboard_app.py
```

## Files
- `market_data.py` — all sourced market/competitive figures + TAM/SAM/SOM calc, with methodology notes and named assumption constants (easy to defend or tweak for Q&A)
- `product_data.py` — synthetic Anaphora product metrics (funnel, compatibility scores), seeded for reproducibility
- `dashboard_app.py` — Streamlit app, 6 charts across "Market Opportunity" and "Simulated Product Metrics"

## Before presenting
- Swap the SOM assumptions in `market_data.py` (PCT_SINGLE, PCT_PAYS_FOR_DATING_APP, capture rates) for real INSEE Paris figures if you want a tighter number.
- The funnel chart for TAM/SAM/SOM uses an illustrative EUR-value proxy for the SOM steps (since SOM is defined in users, not currency) — call this out if asked, don't let it look like a directly comparable currency figure.
