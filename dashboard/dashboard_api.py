"""
Anaphora dashboard backend.

Run with (from inside the dashboard/ folder):
    uvicorn dashboard_api:app --reload
Or from anywhere, pointing --app-dir at this folder:
    uvicorn dashboard_api:app --reload --app-dir dashboard
Then open http://localhost:8000

Requires a .env file (not committed) with:
    OPENAI_API_KEY=sk-...
Place the .env file in this same folder (dashboard/) — see note near
load_dotenv() below for why.
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

import market_data as md
import product_data as pdata

# Resolve all filesystem paths relative to THIS file, not the process's
# working directory. --app-dir only changes where Python imports modules
# from; it does NOT change the cwd, so relative paths like "static" or
# ".env" would otherwise break depending on where uvicorn is launched from.
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

load_dotenv(BASE_DIR / ".env")
client = OpenAI()  # reads OPENAI_API_KEY from the environment automatically

app = FastAPI(title="Anaphora Dashboard API")


# ---------------------------------------------------------------------------
# Data endpoints — every number here is computed live from market_data.py /
# product_data.py, never hardcoded twice. This is what "keep real numbers"
# means in practice: the frontend never invents a figure, it only renders
# what these endpoints return.
# ---------------------------------------------------------------------------

@app.get("/api/kpis")
def get_kpis(pct_single: float = md.DEFAULT_PCT_SINGLE,
             pct_pays: float = md.DEFAULT_PCT_PAYS,
             capture_y3: float = md.DEFAULT_CAPTURE_Y3):
    y3 = md.som_y3(pct_single, pct_pays, capture_y3)
    avg_incumbent_yoy = sum(i["yoy_revenue_pct"] for i in md.INCUMBENTS) / len(md.INCUMBENTS)
    return {
        "tam_2026_eur_bn": md.TAM_EUR_BN[2026],
        "tam_cagr_pct": md.TAM_CAGR * 100,
        "sam_eur_bn": round(md.sam_eur_bn(), 3),
        "som_y3_users": y3,
        "som_y3_capture_pct": capture_y3 * 100,
        "incumbent_avg_yoy_pct": round(avg_incumbent_yoy, 1),
        "pure_yoy_pct": next(g["pct_change"] for g in md.GROWTH_COMPARISON if "PURE" in g["player"]),
    }


@app.get("/api/tam-som")
def get_tam_som(pct_single: float = md.DEFAULT_PCT_SINGLE,
                 pct_pays: float = md.DEFAULT_PCT_PAYS,
                 capture_y3: float = md.DEFAULT_CAPTURE_Y3):
    sam = md.sam_eur_bn()
    y1 = md.som_y1(pct_single, pct_pays)
    y3 = md.som_y3(pct_single, pct_pays, capture_y3)
    return {
        "tam": {"label": "TAM", "sub": "EU dating apps, 2026", "value_eur_bn": md.TAM_EUR_BN[2026]},
        "sam": {"label": "SAM", "sub": "France, paying tier", "value_eur_bn": round(sam, 3)},
        "som_y1": {"label": "SOM Y1", "sub": "Paris launch, paying users", "value_users": y1},
        "som_y3": {"label": "SOM Y3", "sub": "Paris, scaled", "value_users": y3},
        "addressable_paris_pool": round(md.addressable_paris(pct_single, pct_pays)),
        "sliders": {"pct_single": pct_single, "pct_pays": pct_pays, "capture_y3": capture_y3},
    }


@app.get("/api/tam-series")
def get_tam_series():
    return md.tam_series()


@app.get("/api/incumbents")
def get_incumbents():
    return md.INCUMBENTS


@app.get("/api/growth")
def get_growth():
    return md.GROWTH_COMPARISON


@app.get("/api/demand-context")
def get_demand_context():
    return md.DEMAND_CONTEXT


@app.get("/api/product-funnel")
def get_product_funnel():
    return {
        "funnel": pdata.PRODUCT_FUNNEL,
        "drops": [pdata.funnel_drop(i) for i in range(len(pdata.PRODUCT_FUNNEL))],
    }


@app.get("/api/score-chart")
def get_score_chart():
    return {
        "curve": pdata.score_curve(),
        "model": pdata.SCORE_MODEL,
        "mean_lift": pdata.mean_lift(),
    }


# ---------------------------------------------------------------------------
# Ask the data — local rule-based bank first (instant, can't hallucinate
# the sourced figures), OpenAI fallback grounded in the live computed data
# for anything outside that bank.
# ---------------------------------------------------------------------------

class AskRequest(BaseModel):
    query: str
    pct_single: float = md.DEFAULT_PCT_SINGLE
    pct_pays: float = md.DEFAULT_PCT_PAYS
    capture_y3: float = md.DEFAULT_CAPTURE_Y3


def local_answer_bank(pct_single: float, pct_pays: float, capture_y3: float) -> list[dict]:
    y1 = md.som_y1(pct_single, pct_pays)
    y3 = md.som_y3(pct_single, pct_pays, capture_y3)
    pool = round(md.addressable_paris(pct_single, pct_pays))
    sam = md.sam_eur_bn()
    lift = pdata.mean_lift()
    funnel_pct = round(pdata.PRODUCT_FUNNEL[-1]["value"] / pdata.PRODUCT_FUNNEL[0]["value"] * 100, 1)

    return [
        {"keywords": ["som", "bottom", "arrive", "how did you get", "methodology", "calculate"],
         "headline": "SOM is bottom-up from Paris, not a slice of TAM.",
         "body": (f"2.1M Paris population x 80% adult x {round(pct_single*100)}% single x "
                  f"{round(pct_pays*100)}% already paying for a dating app = {pool:,} addressable "
                  f"paying singles. At 1% capture that's {y1:,} paying users in Y1; at "
                  f"{round(capture_y3*100)}% capture, {y3:,} by Y3."),
         "source": "Method: bottom-up. Population base INSEE; paying-tier share Mordor Intelligence 2025."},

        {"keywords": ["tam", "market size", "how big"],
         "headline": f"TAM is EUR {md.TAM_EUR_BN[2026]}B in 2026, growing to EUR {md.TAM_EUR_BN[2034]}B by 2034.",
         "body": (f"That's the Europe dating-apps market (app-based + hybrid matchmaking), "
                  f"{md.TAM_CAGR*100:.2f}% CAGR. We use this definition rather than the narrower "
                  f"'online dating services' figure because hybrid matchmaking players are our real "
                  f"competitive set. SAM (France, paying tier only) is EUR {sam:.2f}B."),
         "source": "MarketDataForecast, Europe Dating Apps Market 2034; Mordor Intelligence (paying-tier share 60.72%)."},

        {"keywords": ["sam", "france", "paying tier"],
         "headline": f"SAM is EUR {sam:.2f}B — France, paying tier only.",
         "body": ("France is ~15.2% of EU27 population, and the paying tier is 60.72% of EU "
                   "dating-app revenue and growing faster than free (11.2% vs 7.53% CAGR). Free/"
                   "ad-supported users are excluded from SAM since we don't compete for them."),
         "source": "Population-weighted share of TAM; Mordor Intelligence 2025."},

        {"keywords": ["incumbent", "tinder", "bumble", "hinge", "competitor", "compet"],
         "headline": "Scale and momentum have come apart.",
         "body": ("Tinder is the biggest (~65M MAU, $1.8B revenue) and shrinking at -5.2% YoY. "
                   "Bumble: ~50M MAU, -11%. Hinge is a third of Tinder's size at ~32M users but "
                   "growing +36% — the intent-led product is winning. That divergence is the opening."),
         "source": "Business of Apps / Match Group Q3 2025; Bumble Inc. Q4 2025. MAU are public estimates, not audited."},

        {"keywords": ["pure", "new entrant", "disrupt", "vulnerable", "swipe"],
         "headline": "PURE grew 95% while all three incumbents fell double digits.",
         "body": ("Same source, same period (Q1-Q3 2025): Tinder -14%, Hinge -12%, Bumble -11%, "
                   "PURE +95% on a feed-based no-swipe design. Users aren't leaving the category — "
                   "they're leaving the swipe."),
         "source": "Useluminix, Dating App Market Share & Size 2026 (Q1-Q3 2025)."},

        {"keywords": ["friend", "compatib", "quality", "differenti", "lift"],
         "headline": f"Friend input moves the mean compatibility score from 62 to 71 (+{lift} pts).",
         "body": ("And it tightens the spread (sigma 15 -> 11) — fewer bad matches, not just better "
                   "averages. This is our core differentiator: friend perspective as a second signal "
                   "on top of self-report. It's a simulated hypothesis, not a measured result — we'd "
                   "validate it in the Paris cohort."),
         "source": "Simulated, seeded model. Labeled synthetic."},

        {"keywords": ["funnel", "conversion", "paid", "paywall", "drop"],
         "headline": f"{funnel_pct}% of signups reach a paid contact unlock.",
         "body": ("500 signups -> 410 complete the AI intake (82%) -> 307 receive a match -> "
                   "276 view match details -> 44 unlock contact. The paywall step is the real "
                   "constraint: most people who look at a match don't pay yet. Intake completion "
                   "at 82% is the healthy part — conversational onboarding holds people."),
         "source": "Simulated product data, seeded (n=500 signups)."},

        {"keywords": ["lonel", "why now", "demand", "household", "single"],
         "headline": "75M single-adult households in the EU, up 16.9% since 2015.",
         "body": ("And 8% of EU adults report no close friends. This is context, not a trend chart: "
                   "the demand isn't the dating category growing, it's the shrinking of the social "
                   "infrastructure that used to make introductions."),
         "source": "Eurostat, OECD Society at a Glance."},
    ]


def match_local_bank(query: str, bank: list[dict]) -> dict | None:
    q = query.lower().strip()
    for entry in bank:
        if any(k in q for k in entry["keywords"]):
            return entry
    return None


def ask_openai(query: str, pct_single: float, pct_pays: float, capture_y3: float) -> dict:
    """Fallback for anything outside the local bank. Grounded in the live
    computed data so it can't invent numbers that contradict the dashboard."""
    context = {
        "kpis": get_kpis(pct_single, pct_pays, capture_y3),
        "tam_som": get_tam_som(pct_single, pct_pays, capture_y3),
        "incumbents": md.INCUMBENTS,
        "growth": md.GROWTH_COMPARISON,
        "demand_context": md.DEMAND_CONTEXT,
        "product_funnel": pdata.PRODUCT_FUNNEL,
        "score_model": pdata.SCORE_MODEL,
    }

    system_prompt = (
        "You are the Anaphora dashboard's data assistant. Answer ONLY using the "
        "JSON data provided below — never invent a figure that isn't in it. If the "
        "question can't be answered from this data, say so plainly and suggest what "
        "the dashboard does cover. Keep answers to 2-3 sentences, plain language, no "
        "jargon. Respond with a short headline (under 12 words) and a body.\n\n"
        f"DATA:\n{context}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        temperature=0.2,
        max_tokens=250,
    )
    text = response.choices[0].message.content.strip()

    # Split into a headline (first line) + body (rest) for consistent rendering
    lines = text.split("\n", 1)
    headline = lines[0].strip("# ").strip()
    body = lines[1].strip() if len(lines) > 1 else ""
    return {"headline": headline, "body": body, "source": "Generated from live dashboard data (gpt-4o-mini)."}


@app.post("/api/ask")
def ask(req: AskRequest):
    bank = local_answer_bank(req.pct_single, req.pct_pays, req.capture_y3)
    hit = match_local_bank(req.query, bank)
    if hit:
        return {"headline": hit["headline"], "body": hit["body"], "source": hit["source"], "via": "local"}

    answer = ask_openai(req.query, req.pct_single, req.pct_pays, req.capture_y3)
    return {**answer, "via": "openai"}


# ---------------------------------------------------------------------------
# Serve the frontend
# ---------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")