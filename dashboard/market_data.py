"""
Market & competitive data for the Anaphora dashboard — single source of
truth, consumed by dashboard_api.py. All formulas here mirror the design
prototype (Anaphora_Dashboard_dc.html) 1:1 so the numbers never drift
between docs, the API, and the frontend.

Methodology notes (repeat these in dashboard_documentation.md / Q&A):
- TAM uses the broader "Europe dating apps market" definition (includes
  app-based + hybrid matchmaking players), not the narrower "online dating
  services" figure, because it better reflects Anaphora's competitive scope.
  Source: MarketDataForecast, Europe Dating Apps Market Size & Share Report
  2034 (accessed Aug 2026).
- MAU figures for incumbents are public estimates, not company-audited
  (companies only disclose paying-subscriber counts).
- The incumbent-vs-new-entrant growth comparison uses one source
  (Useluminix, Q1-Q3 2025) so all four data points are directly comparable.
"""

# --- Sourced constants ------------------------------------------------------

TAM_EUR_BN = {2025: 2.02, 2026: 2.18, 2034: 4.20}
TAM_CAGR = 0.0753  # 7.53%, 2026-2034

FRANCE_POP = 68_000_000
EU27_POP = 448_000_000
FRANCE_SHARE_OF_EU_TAM = FRANCE_POP / EU27_POP  # ~15.2%
PAYING_TIER_SHARE = 0.6072  # Mordor Intelligence 2025

PARIS_POPULATION = 2_100_000
PCT_ADULT = 0.80

# Default slider values (user-adjustable in the UI)
DEFAULT_PCT_SINGLE = 0.35
DEFAULT_PCT_PAYS = 0.15
DEFAULT_CAPTURE_Y3 = 0.03
CAPTURE_Y1 = 0.01  # fixed, not a slider

INCUMBENTS = [
    {"app": "Tinder", "mau_millions_est": 65, "revenue_usd_bn": 1.8, "yoy_revenue_pct": -5.2},
    {"app": "Bumble", "mau_millions_est": 50, "revenue_usd_bn": 1.0, "yoy_revenue_pct": -11.0},
    {"app": "Hinge",  "mau_millions_est": 32, "revenue_usd_bn": 0.58, "yoy_revenue_pct": 36.0},
]

GROWTH_COMPARISON = [
    {"player": "Tinder (incumbent)", "type": "Incumbent", "pct_change": -14.0},
    {"player": "Bumble (incumbent)", "type": "Incumbent", "pct_change": -11.0},
    {"player": "Hinge (incumbent)", "type": "Incumbent", "pct_change": -12.0},
    {"player": "PURE (new entrant, no-swipe)", "type": "New entrant", "pct_change": 95.0},
]

DEMAND_CONTEXT = {
    "eu_single_households_millions": 75.0,
    "single_households_growth_pct_since_2015": 16.9,
    "pct_eu_adults_no_close_friends": 8.0,
}


# --- Derived functions (parameterized so sliders can drive them) -----------

def sam_eur_bn() -> float:
    """France, paying tier only. Not slider-driven — this is a sourced
    calc, not a demo assumption."""
    return TAM_EUR_BN[2026] * FRANCE_SHARE_OF_EU_TAM * PAYING_TIER_SHARE


def addressable_paris(pct_single: float, pct_pays: float) -> float:
    """Bottom-up addressable pool: Paris population x adult share x
    single share x share already paying for a dating app."""
    return PARIS_POPULATION * PCT_ADULT * pct_single * pct_pays


def som_y1(pct_single: float, pct_pays: float) -> int:
    return round(addressable_paris(pct_single, pct_pays) * CAPTURE_Y1)


def som_y3(pct_single: float, pct_pays: float, capture_y3: float) -> int:
    return round(addressable_paris(pct_single, pct_pays) * capture_y3)


def tam_series(start_year: int = 2022, end_year: int = 2031) -> list[dict]:
    """Modeled at TAM_CAGR, anchored on the sourced 2026 figure. Only
    2025/2026/2034 are directly sourced; the rest are interpolated/
    extrapolated - say so wherever this is displayed."""
    return [
        {"year": year, "value": round(TAM_EUR_BN[2026] * ((1 + TAM_CAGR) ** (year - 2026)), 3)}
        for year in range(start_year, end_year + 1)
    ]
