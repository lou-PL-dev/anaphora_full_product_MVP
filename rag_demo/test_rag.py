"""Tests for the baseline generator + retrieval mechanics (profiles.py)."""
from profiles import (
    CANDIDATE_LABELS, STRENGTHS, build_index, generate_profile_pool,
    generate_random_profile, retrieve_similar,
)
import random


def _assert_valid_signal(sig) -> None:
    assert sig.perspective in ("ME", "IDEAL_PARTNER", "US")
    valid_categories = {cat for (persp, cat) in CANDIDATE_LABELS if persp == sig.perspective}
    assert sig.category in valid_categories, f"unexpected category {sig.category!r} for {sig.perspective}"
    assert sig.strength in STRENGTHS
    assert isinstance(sig.label, str) and sig.label


def test_generate_random_profile_signal_shape():
    rng = random.Random(1)
    persona = generate_random_profile(rng, "p1")
    assert persona.id == "p1"
    assert persona.narrative
    assert persona.signals
    for sig in persona.signals:
        _assert_valid_signal(sig)


def test_pool_generation_is_deterministic_given_seed():
    pool_a = generate_profile_pool(10, seed=123)
    pool_b = generate_profile_pool(10, seed=123)
    assert [p.narrative for p in pool_a] == [p.narrative for p in pool_b]
    assert [p.signal_dicts() for p in pool_a] == [p.signal_dicts() for p in pool_b]


def test_pool_generation_varies_across_seeds():
    pool_a = generate_profile_pool(10, seed=1)
    pool_b = generate_profile_pool(10, seed=2)
    assert [p.narrative for p in pool_a] != [p.narrative for p in pool_b]


def test_retrieve_similar_ranks_the_best_match_first():
    pool = generate_profile_pool(30, seed=7)
    index = build_index(pool)
    target = pool[5]
    # Query with the target's own narrative — nothing else in a
    # uniform-random pool of this size should score higher against itself.
    results = retrieve_similar(target.narrative, index, k=5)
    assert results[0][0].id == target.id
    assert results[0][1] >= results[-1][1]


def test_retrieve_similar_respects_k():
    pool = generate_profile_pool(15, seed=3)
    index = build_index(pool)
    results = retrieve_similar("someone warm and family-oriented", index, k=4)
    assert len(results) == 4


def test_retrieve_similar_handles_empty_pool():
    assert retrieve_similar("anything", [], k=5) == []


def test_retrieve_similar_handles_no_overlap_query():
    pool = generate_profile_pool(5, seed=9)
    index = build_index(pool)
    results = retrieve_similar("zzz qqq xyzzy nonoverlapping tokens", index, k=5)
    assert all(score == 0.0 for _, score in results)
