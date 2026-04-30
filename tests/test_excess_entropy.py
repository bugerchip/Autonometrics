"""Tests for the Crutchfield excess-entropy metric."""

import numpy as np
import pytest

from autonometrics.metrics import compute_excess_entropy


def _constant_series(value: int = 1, length: int = 2000) -> np.ndarray:
    return np.full(length, value, dtype=np.int64)


def _iid_uniform_series(alphabet_size: int, length: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, alphabet_size, size=length).astype(np.int64)


def _cycle_series(period: int, length: int) -> np.ndarray:
    return (np.arange(length) % period).astype(np.int64)


def test_constant_series_returns_zero() -> None:
    states = _constant_series()
    env = _iid_uniform_series(2, states.size, seed=0)
    score = compute_excess_entropy(states, env)
    assert score == pytest.approx(0.0, abs=1e-9)


def test_iid_noise_returns_near_zero() -> None:
    states = _iid_uniform_series(4, 5000, seed=1)
    env = _iid_uniform_series(3, states.size, seed=2)
    score = compute_excess_entropy(states, env)
    assert score < 0.3


def test_cycle_period_four_recovers_log2_four() -> None:
    states = _cycle_series(period=4, length=4000)
    env = _iid_uniform_series(2, states.size, seed=3)
    score = compute_excess_entropy(states, env)
    assert score == pytest.approx(2.0, abs=0.1)


def test_cycle_period_eight_recovers_log2_eight() -> None:
    states = _cycle_series(period=8, length=8000)
    env = _iid_uniform_series(2, states.size, seed=4)
    score = compute_excess_entropy(states, env, max_block_length=10)
    assert score == pytest.approx(3.0, abs=0.15)


def test_structured_exceeds_iid() -> None:
    structured = _cycle_series(period=4, length=4000)
    noisy = _iid_uniform_series(4, 4000, seed=5)
    env = _iid_uniform_series(2, 4000, seed=6)
    assert compute_excess_entropy(structured, env) > compute_excess_entropy(noisy, env)


def test_length_mismatch_raises() -> None:
    states = _cycle_series(period=2, length=1000)
    env = _iid_uniform_series(2, 999, seed=7)
    with pytest.raises(ValueError, match="same length"):
        compute_excess_entropy(states, env)


def test_too_short_raises() -> None:
    states = _cycle_series(period=2, length=100)
    env = _iid_uniform_series(2, 100, seed=8)
    with pytest.raises(ValueError, match="series too short"):
        compute_excess_entropy(states, env)


def test_invalid_block_length_raises() -> None:
    states = _cycle_series(period=2, length=1000)
    env = _iid_uniform_series(2, 1000, seed=9)
    with pytest.raises(ValueError, match="max_block_length"):
        compute_excess_entropy(states, env, max_block_length=1)


def test_env_argument_is_ignored() -> None:
    """Two different env streams must produce identical scores."""
    states = _cycle_series(period=5, length=3000)
    env_a = _iid_uniform_series(2, states.size, seed=10)
    env_b = _iid_uniform_series(7, states.size, seed=11)
    assert compute_excess_entropy(states, env_a) == compute_excess_entropy(states, env_b)
