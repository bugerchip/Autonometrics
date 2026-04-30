"""Tests for the Albantakis-style conditional-MI autonomy measure."""

import numpy as np
import pytest

from autonometrics import compute_albantakis


def test_fully_self_determined_system_scores_close_to_one() -> None:
    """S_{t+1} = f(S_t), environment is independent noise → A ≈ 1."""
    rng = np.random.default_rng(42)
    n = 4
    t = 2000
    states = np.empty(t, dtype=np.int64)
    states[0] = 0
    for i in range(1, t):
        states[i] = (states[i - 1] + 1) % n
    env = rng.integers(0, n, size=t)

    score = compute_albantakis(states, env)
    assert score > 0.95


def test_fully_externally_driven_system_scores_close_to_zero() -> None:
    """S_{t+1} = ext_driver + noise, S_t irrelevant → A ≈ 0."""
    rng = np.random.default_rng(123)
    n = 3
    t = 3000
    env = rng.integers(0, n, size=t)
    hidden_noise = rng.integers(0, n, size=t)
    states = np.empty(t, dtype=np.int64)
    states[0] = 0
    for i in range(1, t):
        states[i] = (env[i - 1] + hidden_noise[i - 1]) % n

    score = compute_albantakis(states, env)
    assert score < 0.1


def test_mixed_system_scores_in_between() -> None:
    """Half of the transitions use S_t, the other half are environment-driven."""
    rng = np.random.default_rng(7)
    n = 3
    t = 4000
    env = rng.integers(0, n, size=t)
    mask = rng.random(t) < 0.5
    states = np.empty(t, dtype=np.int64)
    states[0] = 0
    for i in range(1, t):
        if mask[i]:
            states[i] = (states[i - 1] + 1) % n
        else:
            states[i] = env[i - 1]

    score = compute_albantakis(states, env)
    assert 0.15 < score < 0.85


def test_length_mismatch_raises() -> None:
    with pytest.raises(ValueError, match="same length"):
        compute_albantakis(np.array([0, 1, 0]), np.array([0, 1]))


def test_too_short_sequence_raises() -> None:
    with pytest.raises(ValueError, match="at least 2 timesteps"):
        compute_albantakis(np.array([0]), np.array([0]))


def test_constant_state_raises() -> None:
    rng = np.random.default_rng(0)
    states = np.zeros(500, dtype=np.int64)
    env = rng.integers(0, 3, size=500)
    with pytest.raises(ValueError, match="undefined"):
        compute_albantakis(states, env)


def test_score_is_clipped_to_unit_interval() -> None:
    rng = np.random.default_rng(99)
    states = rng.integers(0, 4, size=500)
    env = rng.integers(0, 4, size=500)
    score = compute_albantakis(states, env)
    assert 0.0 <= score <= 1.0
