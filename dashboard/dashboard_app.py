"""
Anaphora — Capstone Round 1 Dashboard
Run with: streamlit run dashboard/dashboard_app.py
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

import market_data as md
import product_data as pd_gen

st.set_page_config(page_title="Anaphora — Market & Product Dashboard", layout="wide")

st.title("Anaphora — AI-Native Matchmaking")
st.caption(
    "Capstone Round 1 dashboard · Market opportunity (sourced) + "
    "simulated product metrics (pre-seed, no real users yet)"
)

# ---------------------------------------------------------------------------
# SECTION A — MARKET OPPORTUNITY
# ---------------------------------------------------------------------------
st.header("Market Opportunity")

# --- Row 1: TAM/SAM/SOM + stat cards ---------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("1. TAM / SAM / SOM")
    funnel_fig = go.Figure(go.Funnel(
        y=["TAM<br>(Europe dating apps market, 2026)",
           "SAM<br>(France, paying tier)",
           "SOM Y1<br>(Paris launch)",
           "SOM Y3<br>(Paris, scaled)"],
        x=[md.TAM_EUR_BN[2026] * 1000,          # in EUR millions for scale
           round(md.SAM_EUR_BN * 1000, 1),
           md.SOM_USERS_Y1 * 0.06,              # illustrative EUR value proxy
           md.SOM_USERS_Y3 * 0.06],
        textinfo="value+percent initial",
    ))
    funnel_fig.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(funnel_fig, use_container_width=True)
    st.caption(
        f"TAM: EUR {md.TAM_EUR_BN[2026]}B (2026, Europe dating apps market). "
        f"SAM: EUR {md.SAM_EUR_BN:.2f}B (France, paying-tier only, ~"
        f"{md.FRANCE_SHARE_OF_EU_TAM*100:.1f}% population-weighted share). "
        f"SOM: {md.SOM_USERS_Y1:,} paying users Y1 → {md.SOM_USERS_Y3:,} by Y3 "
        f"(bottom-up, Paris-first launch — see assumptions in market_data.py)."
    )

with col2:
    st.subheader("Why now")
    st.metric("EU single-adult households", f"{md.DEMAND_CONTEXT['eu_single_households_millions']:.0f}M",
               f"+{md.DEMAND_CONTEXT['single_households_growth_pct_since_2015']:.1f}% since 2015")
    st.metric("EU adults with no close friends", f"{md.DEMAND_CONTEXT['pct_eu_adults_no_close_friends']:.0f}%")

st.divider()

# --- Row 2: Incumbent benchmark + growth trend ------------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("2. Incumbent benchmark — who we're competing for")
    df_inc = pd.DataFrame(md.INCUMBENTS)
    fig_inc = px.bar(
        df_inc, x="app", y="mau_millions_est",
        color="yoy_revenue_pct",
        color_continuous_scale=["#d62728", "#eeeeee", "#2ca02c"],
        labels={"mau_millions_est": "Est. MAU (millions)", "yoy_revenue_pct": "Revenue YoY %"},
        text="mau_millions_est",
    )
    fig_inc.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig_inc, use_container_width=True)
    st.caption("MAU figures are public estimates (not company-audited). Bar color = revenue YoY.")

with col4:
    st.subheader("3. Market growth trend")
    series = md.modeled_tam_series()
    df_trend = pd.DataFrame({"Year": list(series.keys()), "TAM (EUR Bn)": list(series.values())})
    fig_trend = px.line(df_trend, x="Year", y="TAM (EUR Bn)", markers=True)
    fig_trend.add_vline(x=2026, line_dash="dot", annotation_text="today")
    st.plotly_chart(fig_trend, use_container_width=True)
    st.caption(f"Modeled at {md.TAM_CAGR*100:.2f}% CAGR, anchored on 2025/2026/2034 sourced figures.")

st.divider()

# --- Row 3: New entrants disruption signal ----------------------------------
st.subheader("4. New entrants are winning while incumbents decline")
df_growth = pd.DataFrame(md.GROWTH_COMPARISON)
fig_growth = px.bar(
    df_growth, x="player", y="pct_change", color="type",
    color_discrete_map={"Incumbent": "#d62728", "New entrant": "#2ca02c"},
    labels={"pct_change": "Revenue/user growth % (Q1–Q3 2025)"},
)
fig_growth.update_layout(margin=dict(t=10, b=10))
st.plotly_chart(fig_growth, use_container_width=True)
st.caption("Same source/period for all four (Q1–Q3 2025) for direct comparability.")

st.divider()

# ---------------------------------------------------------------------------
# SECTION B — SIMULATED PRODUCT METRICS
# ---------------------------------------------------------------------------
st.header("Simulated Product Metrics")
st.caption("⚠️ Anaphora is pre-seed with no real users. These are simulated to "
           "show what the product would track post-launch.")

col5, col6 = st.columns(2)

with col5:
    st.subheader("5. Onboarding → paid conversion funnel")
    funnel_data = pd_gen.generate_match_funnel()
    fig_prod_funnel = go.Figure(go.Funnel(
        y=list(funnel_data.keys()),
        x=list(funnel_data.values()),
        textinfo="value+percent initial",
    ))
    fig_prod_funnel.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig_prod_funnel, use_container_width=True)

with col6:
    st.subheader("6. Compatibility score: friend-input effect")
    without_friend, with_friend = pd_gen.generate_compatibility_scores()
    fig_scores = go.Figure()
    fig_scores.add_trace(go.Box(y=without_friend, name="Self-report only"))
    fig_scores.add_trace(go.Box(y=with_friend, name="Self-report + friend input"))
    fig_scores.update_layout(yaxis_title="Compatibility score", margin=dict(t=10, b=10))
    st.plotly_chart(fig_scores, use_container_width=True)
    st.caption("Simulated hypothesis (friend input improves match quality), not a measured result.")

st.caption("Data sources: Eurostat, OECD, Mordor Intelligence, MarketDataForecast, "
           "Business of Apps, Useluminix — see market_data.py for full citations.")
