"""
rag_demo — trait distributions used to sample REALISTIC persona profiles.

These are summary statistics, not raw survey rows: no individual's actual
responses are stored or reproduced anywhere in this repo. What's encoded
here is (a) which datasets exist and how big they are, used to justify
"real people answer these instruments at this kind of scale", and (b) the
directional/structural findings from published psychometric analysis of
these instruments, used as sampling parameters so generated personas have
realistic trait co-occurrence instead of independent uniform-random labels.

------------------------------------------------------------------------
SOURCES (accessed 2026-08-30)
------------------------------------------------------------------------
1. Open-Source Psychometrics Project raw data index:
   https://openpsychometrics.org/_rawdata/
   Direct downloads referenced below could not be fetched from this
   environment (openpsychometrics.org is outside this sandbox's network
   allowlist); the file names, sample sizes, and dates below were
   confirmed via a third-party mirror of the same raw-data index
   (haghish/openpsychometrics on GitHub, which republishes these exact
   files "for educational purpose"): https://github.com/haghish/openpsychometrics

   - IPIP-FFM-data-8Nov2018.zip — 1,015,342 respondents, collected
     2016-2018, 50 Likert items (10 per Big Five factor) from Goldberg's
     IPIP Big-Five Factor Markers.
   - ECR-data-1March2018.zip — 51,492 respondents, 36 Likert items from
     the Experiences in Close Relationships (ECR) scale (Brennan, Clark,
     & Shaver, 1998), plus gender/age/country.
     NOTE: the brief this module was built from cites "41,773 responses"
     for this dataset. The 51,492 figure above is what the mirror's index
     reports as the raw file's row count; 41,773 is plausibly the number
     of COMPLETE responses after dropping partial/invalid rows (a common
     preprocessing step openpsychometrics' own codebooks apply), but that
     could not be verified without the actual CSV. Documented here rather
     than silently picking one number.

2. Big Five inter-factor correlation structure ("the Big Five aren't
   fully independent"):
   van der Linden, D., te Nijenhuis, J., & Bakker, A. B. (2010). The
   General Factor of Personality: A meta-analysis of Big Five
   intercorrelations and a criterion-related validity study. Journal of
   Research in Personality, 44(3), 315-327. (K=212 samples, N=144,117 —
   a large-scale meta-analysis, independent of the openpsychometrics
   dataset, confirming the Big Five carry a shared/general factor rather
   than being orthogonal.)
   This module does NOT reproduce that paper's exact correlation matrix
   (not available in this environment) — BIG_FIVE_CORRELATIONS below
   encodes the SIGN and rough relative magnitude (small ~0.1-0.15,
   moderate ~0.2-0.3) of each pairwise relationship as it is consistently
   reported across Big Five psychometric literature, not a precise
   reproduction of any one published table. Treat these as directionally
   grounded, not numerically authoritative.

3. Attachment style prevalence:
   Mickelson, K. D., Kessler, R. C., & Shaver, P. R. (1997). Adult
   attachment in a nationally representative sample. Journal of
   Personality and Social Psychology, 73(5), 1092-1106.
   Reported distribution (the only nationally representative U.S. sample
   ever classified by attachment style): 59% secure, 25% avoidant, 11%
   anxious. IMPORTANT CAVEAT: that study used Hazan & Shaver's original
   3-category forced-choice measure, not the ECR's 2-dimensional
   (anxiety x avoidance) model used here. This module instead classifies
   personas into the ECR tradition's four categories via the standard
   quadrant method — Bartholomew & Horowitz (1991), A Four-Category Model
   of Adult Attachment — and calibrates the anxiety/avoidance thresholds
   so the resulting SECURE share roughly tracks Mickelson et al.'s 59% as
   a sanity check, not an exact target (a 3-category and a 4-category
   classification of even the same population aren't directly comparable).
------------------------------------------------------------------------
"""
from __future__ import annotations

import random

BIG_FIVE_TRAITS = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
TRAIT_LEVELS = ["low", "medium", "high"]

# Approximate, directionally-grounded pairwise correlations between Big
# Five factors (see source #2 above). Index order matches BIG_FIVE_TRAITS.
# Diagonal is 1.0 by definition; matrix is symmetric.
BIG_FIVE_CORRELATIONS: dict[tuple[str, str], float] = {
    ("openness", "conscientiousness"): 0.02,
    ("openness", "extraversion"): 0.20,
    ("openness", "agreeableness"): 0.05,
    ("openness", "neuroticism"): -0.05,
    ("conscientiousness", "extraversion"): 0.10,
    ("conscientiousness", "agreeableness"): 0.20,
    ("conscientiousness", "neuroticism"): -0.25,
    ("extraversion", "agreeableness"): 0.10,
    ("extraversion", "neuroticism"): -0.30,
    ("agreeableness", "neuroticism"): -0.20,
}


def _correlation_matrix() -> list[list[float]]:
    n = len(BIG_FIVE_TRAITS)
    m = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for (a, b), r in BIG_FIVE_CORRELATIONS.items():
        i, j = BIG_FIVE_TRAITS.index(a), BIG_FIVE_TRAITS.index(b)
        m[i][j] = m[j][i] = r
    return m


def _cholesky(matrix: list[list[float]]) -> list[list[float]]:
    """Pure-Python Cholesky decomposition — avoids a numpy dependency for
    what is otherwise a tiny, fixed 5x5 matrix."""
    n = len(matrix)
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                L[i][j] = (matrix[i][i] - s) ** 0.5
            else:
                L[i][j] = (matrix[i][j] - s) / L[j][j]
    return L


_CHOLESKY_L = _cholesky(_correlation_matrix())


# Attachment: sample the two ECR dimensions (anxiety, avoidance) as
# correlated-with-Big-Five continuous scores, then classify into the
# standard four-category quadrant model (source #3 above).
#
# Cross-trait links encoded here (again directional, not numerically
# precise — this pairing between attachment and the Big Five is one of the
# most consistently replicated findings in attachment research):
#   - anxiety loads positively on neuroticism
#   - avoidance loads negatively on agreeableness and extraversion
ATTACHMENT_STYLES = ["secure", "anxious", "avoidant", "fearful_avoidant"]

_ANXIETY_NEUROTICISM_WEIGHT = 0.45
_AVOIDANCE_AGREEABLENESS_WEIGHT = -0.35
_AVOIDANCE_EXTRAVERSION_WEIGHT = -0.20

# Threshold on the z-scale, calibrated (not fit) so the SECURE quadrant
# comes out in the neighbourhood of the 59% reported by Mickelson et al.
# — see the module docstring's caveat that a 3-category study isn't a
# precise target for a 4-category model.
_QUADRANT_CUTPOINT = 0.5


def sample_attachment_style(rng: random.Random, big_five_z: dict[str, float]) -> str:
    """`big_five_z` holds the pre-bucketing continuous z-scores from
    sample_big_five's correlated draw (pass big_five_raw from
    sample_trait_profile, not the low/medium/high labels)."""
    anxiety = (
        _ANXIETY_NEUROTICISM_WEIGHT * big_five_z["neuroticism"]
        + rng.gauss(0, 1) * (1 - abs(_ANXIETY_NEUROTICISM_WEIGHT))
    )
    avoidance = (
        _AVOIDANCE_AGREEABLENESS_WEIGHT * big_five_z["agreeableness"]
        + _AVOIDANCE_EXTRAVERSION_WEIGHT * big_five_z["extraversion"]
        + rng.gauss(0, 1) * 0.6
    )
    high_anxiety = anxiety > _QUADRANT_CUTPOINT
    high_avoidance = avoidance > _QUADRANT_CUTPOINT
    if not high_anxiety and not high_avoidance:
        return "secure"
    if high_anxiety and not high_avoidance:
        return "anxious"
    if not high_anxiety and high_avoidance:
        return "avoidant"
    return "fearful_avoidant"


def sample_trait_profile(rng: random.Random) -> dict:
    """One correlated draw: Big Five levels + an attachment style derived
    from the SAME underlying draw (not sampled independently), so e.g. a
    high-neuroticism persona is more likely to land anxious, matching how
    these traits actually relate to each other in the cited literature."""
    z = {trait: rng.gauss(0, 1) for trait in BIG_FIVE_TRAITS}
    correlated_z = {
        trait: sum(_CHOLESKY_L[i][j] * z[BIG_FIVE_TRAITS[j]] for j in range(i + 1))
        for i, trait in enumerate(BIG_FIVE_TRAITS)
    }

    def bucket(value: float) -> str:
        if value < -0.4307:
            return "low"
        if value > 0.4307:
            return "high"
        return "medium"

    big_five = {trait: bucket(v) for trait, v in correlated_z.items()}
    attachment_style = sample_attachment_style(rng, correlated_z)
    return {"big_five": big_five, "attachment_style": attachment_style}
