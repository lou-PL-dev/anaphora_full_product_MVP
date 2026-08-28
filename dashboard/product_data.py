"""
Synthetic product data for Anaphora (pre-seed, no real users yet).
Clearly labeled as simulated in the dashboard - this demonstrates the
metrics the product WOULD track, using the same profile pool the
matching POC uses.
"""
import numpy as np

rng = np.random.default_rng(42)  # fixed seed = reproducible demo


def generate_match_funnel(n_signups=500):
    """Simulated conversion funnel from signup to paid contact unlock."""
    intake_completed = int(n_signups * rng.uniform(0.78, 0.85))
    matches_generated = int(intake_completed * rng.uniform(0.70, 0.80))
    match_viewed = int(matches_generated * rng.uniform(0.85, 0.95))
    contact_unlocked = int(match_viewed * rng.uniform(0.12, 0.20))  # paywall
    return {
        "Signed up": n_signups,
        "Completed AI intake": intake_completed,
        "Received a match": matches_generated,
        "Viewed match details": match_viewed,
        "Unlocked contact (paid)": contact_unlocked,
    }


def generate_compatibility_scores(n=300):
    """Two distributions: score with vs. without friend-input signal.
    Friend input is modeled as a modest positive shift + tighter spread,
    representing the product hypothesis that friend perspective improves
    match quality. This is a simulated hypothesis, not a measured result -
    say so explicitly when presenting it.
    """
    without_friend = np.clip(rng.normal(loc=62, scale=15, size=n), 0, 100)
    with_friend = np.clip(rng.normal(loc=71, scale=11, size=n), 0, 100)
    return without_friend, with_friend
