"""Tests for the ``PromisedCycle`` adapter."""

from __future__ import annotations

import numpy as np
import pytest

from autonometrics.adapters import PromisedCycle


def test_shapes_match_length() -> None:
    sys = PromisedCycle(length=200, period=4, alphabet=4, p_noise=0.0, seed=0)
    declared, executed = sys.get_declared_executed()
    assert declared.shape == (200,)
    assert executed.shape == (200,)
    assert sys.get_state_history().shape == (200,)
    assert sys.get_env_history().shape == (200,)


def test_p_noise_zero_means_perfect_match() -> None:
    sys = PromisedCycle(length=300, period=5, alphabet=5, p_noise=0.0, seed=0)
    declared, executed = sys.get_declared_executed()
    np.testing.assert_array_equal(declared, executed)


def test_p_noise_one_yields_independent_executed() -> None:
    """At p_noise=1.0 the executed trajectory is uniform on the alphabet,
    so the empirical match rate is close to 1/alphabet, not zero."""
    sys = PromisedCycle(length=4000, period=4, alphabet=4, p_noise=1.0, seed=0)
    declared, executed = sys.get_declared_executed()
    match_rate = float(np.mean(declared == executed))
    expected = 1.0 / 4
    assert abs(match_rate - expected) < 0.03


def test_adversarial_shift_is_deterministic_bijection() -> None:
    sys = PromisedCycle(
        length=400,
        period=4,
        alphabet=5,
        mode="adversarial_shift",
        seed=0,
    )
    declared, executed = sys.get_declared_executed()
    np.testing.assert_array_equal(executed, (declared + 1) % 5)
    assert int(np.sum(declared == executed)) == 0


def test_seed_makes_run_reproducible() -> None:
    a = PromisedCycle(length=500, period=3, alphabet=4, p_noise=0.3, seed=42)
    b = PromisedCycle(length=500, period=3, alphabet=4, p_noise=0.3, seed=42)
    da, ea = a.get_declared_executed()
    db, eb = b.get_declared_executed()
    np.testing.assert_array_equal(da, db)
    np.testing.assert_array_equal(ea, eb)


def test_different_seeds_diverge() -> None:
    a = PromisedCycle(length=500, period=3, alphabet=4, p_noise=0.3, seed=1)
    b = PromisedCycle(length=500, period=3, alphabet=4, p_noise=0.3, seed=2)
    _, ea = a.get_declared_executed()
    _, eb = b.get_declared_executed()
    assert not np.array_equal(ea, eb)


def test_state_history_returns_executed() -> None:
    sys = PromisedCycle(length=100, period=4, alphabet=4, p_noise=0.2, seed=0)
    _, executed = sys.get_declared_executed()
    np.testing.assert_array_equal(sys.get_state_history(), executed)


def test_env_history_is_constant_placeholder() -> None:
    sys = PromisedCycle(length=100, period=4, alphabet=4, seed=0)
    env = sys.get_env_history()
    assert np.all(env == 0)


def test_rejects_invalid_mode() -> None:
    with pytest.raises(ValueError, match="Unknown mode"):
        PromisedCycle(length=100, period=4, alphabet=4, mode="oops", seed=0)


def test_rejects_invalid_p_noise() -> None:
    with pytest.raises(ValueError, match="p_noise"):
        PromisedCycle(length=100, period=4, alphabet=4, p_noise=1.5, seed=0)


def test_rejects_alphabet_too_small() -> None:
    with pytest.raises(ValueError, match="alphabet"):
        PromisedCycle(length=100, period=1, alphabet=1, seed=0)


def test_rejects_period_out_of_range() -> None:
    with pytest.raises(ValueError, match="period"):
        PromisedCycle(length=100, period=10, alphabet=4, seed=0)


def test_rejects_length_too_small() -> None:
    with pytest.raises(ValueError, match="length"):
        PromisedCycle(length=1, period=1, alphabet=2, seed=0)


def test_get_state_history_returns_copy() -> None:
    sys = PromisedCycle(length=100, period=4, alphabet=4, p_noise=0.0, seed=0)
    h = sys.get_state_history()
    h[0] = -999
    np.testing.assert_array_equal(sys.get_state_history()[0:1], np.array([0]))


def test_get_declared_executed_returns_copies() -> None:
    sys = PromisedCycle(length=100, period=4, alphabet=4, p_noise=0.0, seed=0)
    d, e = sys.get_declared_executed()
    d[0] = -999
    e[0] = -999
    d2, e2 = sys.get_declared_executed()
    assert d2[0] == 0
    assert e2[0] == 0


def test_replay_returns_unperturbed_slice() -> None:
    """PromisedCycle is state-perturbation-insensitive by construction."""
    sys = PromisedCycle(length=200, period=4, alphabet=4, p_noise=0.2, seed=0)
    _, executed = sys.get_declared_executed()
    replay = sys.replay_from_perturbation(t_star=50, n_steps=64)
    np.testing.assert_array_equal(replay, executed[51:115])


def test_replay_rejects_out_of_range_t_star() -> None:
    sys = PromisedCycle(length=100, period=4, alphabet=4, p_noise=0.0, seed=0)
    with pytest.raises(ValueError, match="t_star"):
        sys.replay_from_perturbation(t_star=99, n_steps=10)


def test_replay_rejects_excessive_horizon() -> None:
    sys = PromisedCycle(length=100, period=4, alphabet=4, p_noise=0.0, seed=0)
    with pytest.raises(ValueError, match="t_star \\+ n_steps"):
        sys.replay_from_perturbation(t_star=50, n_steps=80)
