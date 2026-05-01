"""Tests for the PeriodicCycle benchmark adapter."""

import numpy as np
import pytest

from autonometrics import Autonometer
from autonometrics.benchmarks import PeriodicCycle


def test_state_history_is_periodic() -> None:
    cycle = PeriodicCycle(period=4, n_steps=20, seed=0)
    states = cycle.get_state_history()
    expected = np.array([0, 1, 2, 3] * 5, dtype=np.int64)
    np.testing.assert_array_equal(states, expected)


def test_env_history_alphabet_respected() -> None:
    cycle = PeriodicCycle(period=3, n_steps=600, env_alphabet=5, seed=0)
    env = cycle.get_env_history()
    assert env.min() >= 0
    assert env.max() < 5


def test_reproducible_env_with_same_seed() -> None:
    a = PeriodicCycle(period=3, n_steps=600, env_alphabet=4, seed=42).get_env_history()
    b = PeriodicCycle(period=3, n_steps=600, env_alphabet=4, seed=42).get_env_history()
    np.testing.assert_array_equal(a, b)


def test_state_independent_of_seed() -> None:
    a = PeriodicCycle(period=4, n_steps=600, seed=1).get_state_history()
    b = PeriodicCycle(period=4, n_steps=600, seed=2).get_state_history()
    np.testing.assert_array_equal(a, b)


def test_get_state_history_returns_copy() -> None:
    cycle = PeriodicCycle(period=4, n_steps=300, seed=0)
    out = cycle.get_state_history()
    out[0] = -999
    assert cycle.get_state_history()[0] == 0


def test_period_two_with_random_env_yields_high_closure() -> None:
    """A period-2 cycle is fully determined by its previous state."""
    cycle = PeriodicCycle(period=2, n_steps=2000, env_alphabet=3, seed=0)
    profile = Autonometer(metrics=["albantakis"]).measure(cycle)
    assert profile.ratio_endo_total is not None
    assert profile.ratio_endo_total >= 0.95


def test_smoke_with_autonometer_full_profile() -> None:
    cycle = PeriodicCycle(period=4, n_steps=2000, env_alphabet=3, seed=0)
    profile = Autonometer(metrics=["albantakis", "memory"]).measure(cycle)
    assert profile.ratio_endo_total is not None
    assert 0.0 <= profile.ratio_endo_total <= 1.0
    assert profile.memory_endo_ratio is not None
    assert 0.0 <= profile.memory_endo_ratio <= 1.0


def test_rejects_invalid_period() -> None:
    with pytest.raises(ValueError, match="period"):
        PeriodicCycle(period=1, n_steps=100)


def test_rejects_invalid_n_steps() -> None:
    with pytest.raises(ValueError, match="n_steps"):
        PeriodicCycle(period=2, n_steps=1)


def test_rejects_invalid_env_alphabet() -> None:
    with pytest.raises(ValueError, match="env_alphabet"):
        PeriodicCycle(period=2, n_steps=100, env_alphabet=1)
