"""Tests for the Fernandez-Gershenson autopoietic ratio measure.

The complexity ``C(x) = 4 * E(x) * (1 - E(x))`` peaks at normalised
entropy ``E = 0.5`` (a balanced mix of order and disorder), *not* at
uniform distributions. So the canonical tests build binary sequences
with a controlled fraction of ``1`` s to hit specific points on the
``C`` curve.
"""

import numpy as np
import pytest

from autonometrics import compute_autopoietic_ratio


def _binary_with_fraction(n: int, ones_fraction: float) -> np.ndarray:
    """Return a length-``n`` int64 array whose fraction of ones is exact."""
    arr = np.zeros(n, dtype=np.int64)
    n_ones = int(round(n * ones_fraction))
    arr[:n_ones] = 1
    return arr


def test_matched_complexity_gives_ratio_close_to_one() -> None:
    """Both sequences at E ~ 0.5 (C ~ 1): ratio ~ 1."""
    states = _binary_with_fraction(10_000, 0.11)
    env = _binary_with_fraction(10_000, 0.11)
    a = compute_autopoietic_ratio(states, env)
    assert 0.9 < a < 1.1


def test_complex_system_in_simpler_environment_gives_ratio_above_one() -> None:
    """System near C=1 (p=0.11), env near C=0.11 (p=0.40): A > 5."""
    states = _binary_with_fraction(10_000, 0.11)
    env = _binary_with_fraction(10_000, 0.40)
    a = compute_autopoietic_ratio(states, env)
    assert a > 5.0


def test_simple_system_in_more_complex_environment_gives_ratio_below_one() -> None:
    """System near C=0.11 (p=0.40), env near C=1 (p=0.11): A < 0.2."""
    states = _binary_with_fraction(10_000, 0.40)
    env = _binary_with_fraction(10_000, 0.11)
    a = compute_autopoietic_ratio(states, env)
    assert a < 0.2


def test_uniform_binary_environment_raises() -> None:
    """p=0.5 on both alphabet symbols gives E=1, so C(env)=0 and A is undefined."""
    states = _binary_with_fraction(10_000, 0.11)
    env = _binary_with_fraction(10_000, 0.50)
    with pytest.raises(ValueError, match="C\\(env\\) is zero"):
        compute_autopoietic_ratio(states, env)


def test_constant_environment_raises() -> None:
    rng = np.random.default_rng(3)
    states = rng.integers(0, 4, size=500)
    env = np.zeros(500, dtype=np.int64)
    with pytest.raises(ValueError, match="C\\(env\\) is zero"):
        compute_autopoietic_ratio(states, env)


def test_constant_system_returns_zero() -> None:
    """A constant system has zero complexity; the ratio is well-defined as 0."""
    states = np.zeros(500, dtype=np.int64)
    env = _binary_with_fraction(500, 0.11)
    a = compute_autopoietic_ratio(states, env)
    assert a == 0.0


def test_length_mismatch_raises() -> None:
    with pytest.raises(ValueError, match="same length"):
        compute_autopoietic_ratio(np.array([0, 1, 0]), np.array([0, 1]))


def test_too_short_sequence_raises() -> None:
    with pytest.raises(ValueError, match="at least 2 timesteps"):
        compute_autopoietic_ratio(np.array([0]), np.array([0]))


def test_ratio_is_non_negative() -> None:
    rng = np.random.default_rng(5)
    for seed in range(3):
        r = np.random.default_rng(seed)
        states = r.integers(0, 5, size=2000)
        env = rng.integers(0, 4, size=2000)
        try:
            a = compute_autopoietic_ratio(states, env)
        except ValueError:
            continue
        assert a >= 0.0
