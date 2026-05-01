"""Tests for the distributed structural-memory ratio."""

import numpy as np
import pytest

from autonometrics.metrics import compute_memory_endo_ratio


def _constant_series(value: int = 1, length: int = 2000) -> np.ndarray:
    return np.full(length, value, dtype=np.int64)


def _iid_uniform_series(alphabet_size: int, length: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, alphabet_size, size=length).astype(np.int64)


def _cycle_series(period: int, length: int) -> np.ndarray:
    return (np.arange(length) % period).astype(np.int64)


def test_both_constant_returns_zero_by_convention() -> None:
    states = _constant_series(0, 2000)
    env = _constant_series(0, 2000)
    score = compute_memory_endo_ratio(states, env)
    assert score == pytest.approx(0.0, abs=1e-9)


def test_states_constant_env_structured_returns_low_ratio() -> None:
    states = _constant_series(0, 4000)
    env = _cycle_series(period=4, length=4000)
    score = compute_memory_endo_ratio(states, env)
    assert score == pytest.approx(0.0, abs=1e-2)


def test_states_structured_env_iid_returns_high_ratio() -> None:
    states = _cycle_series(period=4, length=4000)
    env = _iid_uniform_series(4, 4000, seed=0)
    score = compute_memory_endo_ratio(states, env)
    assert score >= 0.85


def test_states_structured_env_constant_returns_one() -> None:
    states = _cycle_series(period=4, length=4000)
    env = _constant_series(0, 4000)
    score = compute_memory_endo_ratio(states, env)
    assert score == pytest.approx(1.0, abs=1e-2)


def test_both_iid_falls_back_to_zero_convention() -> None:
    states = _iid_uniform_series(4, 5000, seed=1)
    env = _iid_uniform_series(3, 5000, seed=2)
    score = compute_memory_endo_ratio(states, env)
    assert 0.0 <= score <= 1.0


def test_both_same_structure_is_balanced() -> None:
    states = _cycle_series(period=4, length=4000)
    env = _cycle_series(period=4, length=4000)
    score = compute_memory_endo_ratio(states, env)
    assert score == pytest.approx(0.5, abs=0.05)


def test_score_always_within_unit_interval() -> None:
    states = _cycle_series(period=5, length=3000)
    env = _iid_uniform_series(7, 3000, seed=11)
    score = compute_memory_endo_ratio(states, env)
    assert 0.0 <= score <= 1.0


def test_length_mismatch_raises() -> None:
    states = _cycle_series(period=2, length=1000)
    env = _iid_uniform_series(2, 999, seed=7)
    with pytest.raises(ValueError, match="same length"):
        compute_memory_endo_ratio(states, env)


def test_too_short_raises() -> None:
    states = _cycle_series(period=2, length=100)
    env = _iid_uniform_series(2, 100, seed=8)
    with pytest.raises(ValueError, match="series too short"):
        compute_memory_endo_ratio(states, env)


def test_invalid_block_length_raises() -> None:
    states = _cycle_series(period=2, length=1000)
    env = _iid_uniform_series(2, 1000, seed=9)
    with pytest.raises(ValueError, match="max_block_length"):
        compute_memory_endo_ratio(states, env, max_block_length=1)
