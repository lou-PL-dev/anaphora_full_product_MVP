"""
Market & competitive data for the Anaphora capstone dashboard.

Methodology notes (put these in dashboard_documentation.md too):
- TAM uses the broader "Europe dating apps market" definition (includes
  app-based + hybrid matchmaking players), not the narrower "online dating
  services" figure, because it better reflects Anaphora's actual competitive
  scope. Source: MarketDataForecast, Europe Dating Apps Market Size & Share
  Report 2034 (accessed Aug 2026).
- MAU figures for incumbents are not consistently audited (companies only
  disclose paying-subscriber counts). Figures below are best-available
  public estimates as of 2026 and are labeled "est." in the dashboard.
- The incumbent-vs-new-entrant growth comparison uses a single source
  (Luminix, Q1-Q3 2025) so all four data points are directly comparable.
"""

# --- TAM / SAM / SOM (EUR, billions unless noted) -------------------------

TAM_EUR_BN = {
    2025: 2.02,   # backcast from 2026 figure using stated CAGR
    2026: 2.18,   # Europe dating apps market, MarketDataForecast
    2034: 4.20,   # projected, same source
}
TAM_CAGR = 0.0753  # 7.53%, 2026-2034

# SAM: France's share of the EU dating-apps TAM, approximated by population
# share (France ~68M / EU27 ~448M ~= 15.2%). Paying-tier only, since that's
# Anaphora's target segment (paying tier = 60.72% of EU dating-app revenue,
# Mordor Intelligence 2025).
FRANCE_POP = 68_000_000
EU27_POP = 448_000_000
FRANCE_SHARE_OF_EU_TAM = FRANCE_POP / EU27_POP
PAYING_TIER_SHARE = 0.6072

SAM_EUR_BN = TAM_EUR_BN[2026] * FRANCE_SHARE_OF_EU_TAM * PAYING_TIER_SHARE

# SOM: bottom-up from a Paris-first launch. All assumptions are named
# constants below so they're easy to defend/tune in Q&A.
PARIS_POPULATION = 2_100_000
PCT_ADULT = 0.80                 # share of population that is adult
PCT_SINGLE = 0.35                # share of adults who are single (assumption
                                  # - Paris has an unusually high single-
                                  # person-household rate; adjust with INSEE
                                  # data if you want a tighter number)
PCT_PAYS_FOR_DATING_APP = 0.15   # share of singles currently paying for any
                                  # dating app subscription
CAPTURE_RATE_Y1 = 0.01           # 1% of that addressable pool in year 1
CAPTURE_RATE_Y3 = 0.03           # 3% by year 3

paris_addressable = (
    PARIS_POPULATION * PCT_ADULT * PCT_SINGLE * PCT_PAYS_FOR_DATING_APP
)
SOM_USERS_Y1 = round(paris_addressable * CAPTURE_RATE_Y1)
SOM_USERS_Y3 = round(paris_addressable * CAPTURE_RATE_Y3)

# --- Incumbent benchmark (chart 2: "who we're stealing from") -------------
# Sources: Business of Apps (Tinder), Mordor Intelligence / Bumble Inc. Q4
# 2025 earnings (Bumble), Business of Apps / Match Group Q3 2024-25 (Hinge).
INCUMBENTS = [
    {"app": "Tinder", "mau_millions_est": 65, "revenue_usd_bn": 1.8, "yoy_revenue_pct": -5.2},
    {"app": "Bumble", "mau_millions_est": 50, "revenue_usd_bn": 1.0, "yoy_revenue_pct": -11.0},
    {"app": "Hinge",  "mau_millions_est": 32, "revenue_usd_bn": 0.58, "yoy_revenue_pct": 36.0},
]

# --- Market growth trend (chart 3) -----------------------------------------
# Modeled series 2022-2031 anchored on published 2025/2026/2034 figures and
# the stated CAGR - smooths the line for the chart; only 2025/2026/2034 are
# directly sourced, the rest are interpolated/extrapolated at 7.53% CAGR.
def modeled_tam_series(start_year=2022, end_year=2031):
    series = {}
    for year in range(start_year, end_year + 1):
        exp = year - 2026
        series[year] = round(TAM_EUR_BN[2026] * ((1 + TAM_CAGR) ** exp), 3)
    return series

# --- New entrants vs incumbents (chart 4) -----------------------------------
# Same source, same period (Q1-Q3 2025), for direct comparability.
# Source: Useluminix Dating App Market Share & Size 2026.
GROWTH_COMPARISON = [
    {"player": "Tinder (incumbent)", "type": "Incumbent", "pct_change": -14.0},
    {"player": "Bumble (incumbent)", "type": "Incumbent", "pct_change": -11.0},
    {"player": "Hinge (incumbent)", "type": "Incumbent", "pct_change": -12.0},
    {"player": "PURE (new entrant, no-swipe)", "type": "New entrant", "pct_change": 95.0},
]

# --- Loneliness / demand-driver context (stat cards, not a chart) ---------
DEMAND_CONTEXT = {
    "eu_single_households_millions": 75.0,
    "single_households_growth_pct_since_2015": 16.9,
    "pct_eu_adults_no_close_friends": 8.0,
}
