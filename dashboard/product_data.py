"""
Simulated Anaphora product data (pre-seed, no real users yet).
Numbers are fixed/seeded to match the agreed demo scenario in the design
(Anaphora_Dashboard_dc.html) — not randomly regenerated on each run, so the
dashboard, the docs, and the "ask the data" answers always agree.
"""
import math

# Fixed funnel scenario — 500 simulated signups.
PRODUCT_FUNNEL = [
    {"label": "Signed up", "value": 500},
    {"label": "Completed AI intake", "value": 410},
    {"label": "Received a match", "value": 307},
    {"label": "Viewed match details", "value": 276},
    {"label": "Unlocked contact (paid)", "value": 44},
]

# Compatibility score model: self-report only vs. + friend input.
# Modeled as two gaussians (not sampled — deterministic curve so the
# chart, the "+9 pts mean lift" headline, and repeat runs always match).
SCORE_MODEL = {
    "without_friend": {"mean": 62, "stdev": 15},
    "with_friend": {"mean": 71, "stdev": 11},
}


def funnel_drop(step_index: int) -> dict:
    """Drop-off between the given step and the previous one."""
    if step_index <= 0:
        return {
            "from": None,
            "to": PRODUCT_FUNNEL[0]["label"],
            "dropped": 0,
            "drop_pct": 0,
            "note": "500 simulated signups is the top of the funnel — "
                    "the seeded base for every step below.",
        }
    prev = PRODUCT_FUNNEL[step_index - 1]
    step = PRODUCT_FUNNEL[step_index]
    dropped = prev["value"] - step["value"]
    drop_pct = round((1 - step["value"] / prev["value"]) * 100)
    note = f"{prev['label']} → {step['label']}: {dropped} people drop off ({drop_pct}%)."
    if step_index == len(PRODUCT_FUNNEL) - 1:
        note += " This is the paywall — the step worth optimising first."
    return {"from": prev["label"], "to": step["label"], "dropped": dropped,
            "drop_pct": drop_pct, "note": note}


def score_curve(bins=range(25, 96, 10)) -> list[dict]:
    """Gaussian density (not a sampled histogram) for each score bin, for
    both distributions — matches the SVG curve in the design 1:1."""
    def gaussian(x, mu, sd):
        return math.exp(-((x - mu) ** 2) / (2 * sd * sd))

    a = SCORE_MODEL["without_friend"]
    b = SCORE_MODEL["with_friend"]
    return [
        {
            "score": c,
            "without_friend": round(gaussian(c, a["mean"], a["stdev"]), 4),
            "with_friend": round(gaussian(c, b["mean"], b["stdev"]), 4),
        }
        for c in bins
    ]


def mean_lift() -> int:
    return SCORE_MODEL["with_friend"]["mean"] - SCORE_MODEL["without_friend"]["mean"]
