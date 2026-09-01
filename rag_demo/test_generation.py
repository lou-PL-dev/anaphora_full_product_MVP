"""Tests for the trait-grounded generator (generate_personas.py /
trait_distributions.py). The full LLM pipeline (generate_persona /
generate_persona_pool) needs a real OPENAI_API_KEY and network access, so
those two are skipped unless one is configured — everything else here
(sampling, prompt construction, the offline narrative, and the
extraction-result -> Signal mapping that's the one genuinely new piece of
logic beyond what test_rag.py already covers) is fully exercised without
either."""
import random

import pytest

from generate_personas import (
    ATTACHMENT_DESCRIPTIONS, BIG_FIVE_DESCRIPTIONS, NARRATIVE_CATEGORIES, STYLE_SEED_EXAMPLES,
    build_narrative_prompt, describe_trait_profile, extraction_result_to_signals,
    generate_candidate_pool, generate_persona_pool, offline_narrative, offline_self_narrative,
    sample_category_ingredients,
)
from profiles import CANDIDATE_LABELS, STRENGTHS
from trait_distributions import ATTACHMENT_STYLES, BIG_FIVE_TRAITS, TRAIT_LEVELS, sample_trait_profile

try:
    from app.config import settings
    _HAS_LLM_CREDENTIALS = bool(settings.openai_api_key)
except Exception:
    _HAS_LLM_CREDENTIALS = False


def _assert_valid_signal(sig) -> None:
    assert sig.perspective in ("ME", "IDEAL_PARTNER")
    valid_categories = {cat for (persp, cat) in CANDIDATE_LABELS if persp == sig.perspective}
    assert sig.category in valid_categories, f"unexpected category {sig.category!r} for {sig.perspective}"
    assert sig.strength in STRENGTHS
    assert isinstance(sig.label, str) and sig.label


def test_sample_trait_profile_shape():
    rng = random.Random(1)
    for _ in range(200):
        profile = sample_trait_profile(rng)
        assert set(profile["big_five"]) == set(BIG_FIVE_TRAITS)
        for level in profile["big_five"].values():
            assert level in TRAIT_LEVELS
        assert profile["attachment_style"] in ATTACHMENT_STYLES


def test_big_five_tertiles_are_roughly_balanced():
    """Sanity check on sample_trait_profile's marginals — each trait should
    land in each tertile roughly a third of the time, confirming the
    Cholesky-correlated draw didn't skew any single trait's own
    distribution while inducing cross-trait correlation."""
    rng = random.Random(5)
    counts = {t: {"low": 0, "medium": 0, "high": 0} for t in BIG_FIVE_TRAITS}
    n = 3000
    for _ in range(n):
        profile = sample_trait_profile(rng)
        for t, level in profile["big_five"].items():
            counts[t][level] += 1
    for t in BIG_FIVE_TRAITS:
        for level in TRAIT_LEVELS:
            share = counts[t][level] / n
            assert 0.25 < share < 0.42, f"{t}/{level} share {share:.2%} is not roughly a third"


def test_high_neuroticism_correlates_with_anxious_and_fearful_attachment():
    """The one statistical claim this whole module exists to encode: per
    the cited literature, attachment anxiety loads on neuroticism, so
    high-neuroticism personas should land anxious/fearful noticeably more
    often than the overall population baseline."""
    rng = random.Random(11)
    n = 4000
    baseline = {"anxious": 0, "fearful_avoidant": 0}
    high_neurotic = {"anxious": 0, "fearful_avoidant": 0}
    high_neurotic_total = 0
    for _ in range(n):
        profile = sample_trait_profile(rng)
        style = profile["attachment_style"]
        if style in baseline:
            baseline[style] += 1
        if profile["big_five"]["neuroticism"] == "high":
            high_neurotic_total += 1
            if style in high_neurotic:
                high_neurotic[style] += 1

    baseline_rate = (baseline["anxious"] + baseline["fearful_avoidant"]) / n
    high_neurotic_rate = (high_neurotic["anxious"] + high_neurotic["fearful_avoidant"]) / high_neurotic_total
    assert high_neurotic_rate > baseline_rate + 0.10, (
        f"expected high-neuroticism anxious/fearful rate ({high_neurotic_rate:.1%}) to clear "
        f"the baseline ({baseline_rate:.1%}) by a real margin"
    )


def test_describe_trait_profile_mentions_every_sampled_trait():
    rng = random.Random(2)
    profile = sample_trait_profile(rng)
    description = describe_trait_profile(profile)
    for trait, level in profile["big_five"].items():
        assert BIG_FIVE_DESCRIPTIONS[(trait, level)] in description
    assert ATTACHMENT_DESCRIPTIONS[profile["attachment_style"]] in description


def test_offline_narrative_is_well_formed():
    rng = random.Random(4)
    profile = sample_trait_profile(rng)
    narrative = offline_narrative(profile)
    assert isinstance(narrative, str)
    assert "I'm looking for someone" in narrative
    assert "As for me" in narrative
    # every trait's descriptive phrase should show up somewhere in the text
    for trait, level in profile["big_five"].items():
        assert BIG_FIVE_DESCRIPTIONS[(trait, level)] in narrative


def test_build_narrative_prompt_carries_style_seeds_not_content():
    rng = random.Random(6)
    profile = sample_trait_profile(rng)
    messages = build_narrative_prompt(profile, STYLE_SEED_EXAMPLES)
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    for example in STYLE_SEED_EXAMPLES:
        assert example in messages[0]["content"]
    # the trait sketch belongs in the user turn, not hardcoded style text
    assert describe_trait_profile(profile) in messages[1]["content"]


def test_extraction_result_to_signals_shape():
    from app.schemas import ExtractionResult, PerspectiveBlueprint, SignalItem, Strength

    result = ExtractionResult(
        ideal_partner=PerspectiveBlueprint(
            personality=[SignalItem(label="Warm", strength=Strength.strong_preference, evidence_text="checks in")],
            dealbreakers=[SignalItem(label="No smoking", strength=Strength.hard_requirement)],
        ),
        me=PerspectiveBlueprint(values=[SignalItem(label="Growth", strength=Strength.preference)]),
        narrative="Warm, and won't budge on smoking.",
    )
    signals = extraction_result_to_signals(result)
    assert len(signals) == 3
    for sig in signals:
        _assert_valid_signal(sig)
    ideal = [s for s in signals if s.perspective == "IDEAL_PARTNER"]
    me = [s for s in signals if s.perspective == "ME"]
    assert {s.category for s in ideal} == {"personality", "dealbreakers"}
    assert {s.category for s in me} == {"values"}


def test_sample_category_ingredients_covers_every_narrative_category():
    rng = random.Random(3)
    for perspective in ("ME", "IDEAL_PARTNER"):
        ingredients = sample_category_ingredients(rng, perspective)
        assert set(ingredients) == set(NARRATIVE_CATEGORIES)
        for category, labels in ingredients.items():
            assert len(labels) == 2
            assert len(set(labels)) == len(labels)  # distinct, no repeats within a category
            for label in labels:
                assert label in CANDIDATE_LABELS[(perspective, category)]


def test_sample_category_ingredients_clamps_to_pool_size():
    """count higher than a category's label pool must not raise or repeat
    labels — just return everything the pool has."""
    rng = random.Random(9)
    ingredients = sample_category_ingredients(rng, "ME", count=1000)
    for category, labels in ingredients.items():
        assert set(labels) == set(CANDIDATE_LABELS[("ME", category)])


def test_offline_self_narrative_includes_ingredients():
    rng = random.Random(7)
    profile = sample_trait_profile(rng)
    ingredients = sample_category_ingredients(rng, "ME")
    narrative = offline_self_narrative(profile, ingredients)
    for labels in ingredients.values():
        for label in labels:
            assert label in narrative


@pytest.mark.skipif(not _HAS_LLM_CREDENTIALS, reason="needs a real OPENAI_API_KEY to call the LLM + extraction chain")
def test_generate_persona_pool_end_to_end():
    pool = generate_persona_pool(2, seed=1, use_llm=True)
    assert len(pool) == 2
    for persona in pool:
        assert persona.narrative
        assert persona.signals
        for sig in persona.signals:
            _assert_valid_signal(sig)


@pytest.mark.skipif(not _HAS_LLM_CREDENTIALS, reason="needs a real OPENAI_API_KEY to call the LLM + extraction chain")
def test_generate_candidate_pool_reaches_readiness_bar():
    """The whole point of feeding category_ingredients into the narrative
    prompt: a generated candidate's ME signals should be rich enough to
    satisfy the SAME completeness bar anaphora_backend/app/readiness.py
    requires of real users (mandatory categories + at least 5 of 7) — before
    this fix, candidates only ever had material for personality and
    relationship_dynamic and essentially never cleared this bar."""
    from app.readiness import CORE_CATEGORIES, MANDATORY_CATEGORIES, MIN_CATEGORIES_PER_SIDE

    pool = generate_candidate_pool(3, seed=2, use_llm=True)
    cleared = 0
    for persona in pool:
        covered = {s.category for s in persona.signals if s.category in CORE_CATEGORIES}
        if MANDATORY_CATEGORIES.issubset(covered) and len(covered) >= MIN_CATEGORIES_PER_SIDE:
            cleared += 1
    assert cleared >= 2, f"expected most of a 3-candidate pool to clear the readiness bar, only {cleared} did"
