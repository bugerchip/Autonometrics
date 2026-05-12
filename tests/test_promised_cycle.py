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


# --- p_env (independent declared-channel noise) ----------------------------


def test_p_env_zero_default_preserves_pure_cycle() -> None:
    """With p_env=0 (default) the declared channel is exactly the cycle."""
    sys = PromisedCycle(length=120, period=4, alphabet=4, p_noise=0.5, seed=7)
    declared, _ = sys.get_declared_executed()
    expected = (np.arange(120) % 4).astype(np.int64)
    np.testing.assert_array_equal(declared, expected)


def test_p_env_zero_explicit_matches_default() -> None:
    """Passing p_env=0 explicitly is byte-for-byte identical to the default."""
    a = PromisedCycle(length=300, period=3, alphabet=5, p_noise=0.4, seed=9)
    b = PromisedCycle(length=300, period=3, alphabet=5, p_noise=0.4, p_env=0.0, seed=9)
    da, ea = a.get_declared_executed()
    db, eb = b.get_declared_executed()
    np.testing.assert_array_equal(da, db)
    np.testing.assert_array_equal(ea, eb)


def test_p_env_one_yields_uniform_declared() -> None:
    """With p_env=1 every step is replaced; declared ≈ uniform on alphabet."""
    sys = PromisedCycle(length=4000, period=2, alphabet=4, p_noise=0.0, p_env=1.0, seed=0)
    declared, _ = sys.get_declared_executed()
    counts = np.bincount(declared, minlength=4)
    freqs = counts / counts.sum()
    assert np.all(np.abs(freqs - 0.25) < 0.03)


def test_p_env_one_p_noise_zero_executed_tracks_declared() -> None:
    """With p_noise=0 the executed channel still equals declared
    even when declared has been fully randomised by p_env=1."""
    sys = PromisedCycle(length=500, period=2, alphabet=4, p_noise=0.0, p_env=1.0, seed=3)
    declared, executed = sys.get_declared_executed()
    np.testing.assert_array_equal(declared, executed)


def test_p_env_and_p_noise_are_independent_streams() -> None:
    """The env and noise masks come from independent draws of the same RNG.

    Specifically, with p_env=0.5 we expect declared to differ from the
    base cycle on roughly half the steps, regardless of p_noise.
    """
    rng_seed = 11
    base = (np.arange(2000) % 4).astype(np.int64)
    sys = PromisedCycle(length=2000, period=4, alphabet=4, p_noise=0.0, p_env=0.5, seed=rng_seed)
    declared, _ = sys.get_declared_executed()
    diff_rate = float(np.mean(declared != base))
    # Half the positions touched by env_mask, of which 1 - 1/alphabet differ
    # from the base cycle on average → ~0.5 * 0.75 = 0.375.
    assert 0.30 < diff_rate < 0.45


def test_p_env_property_is_exposed() -> None:
    sys = PromisedCycle(length=100, period=4, alphabet=4, p_env=0.25, seed=0)
    assert sys.p_env == pytest.approx(0.25)


def test_rejects_invalid_p_env() -> None:
    with pytest.raises(ValueError, match="p_env"):
        PromisedCycle(length=100, period=4, alphabet=4, p_env=-0.1, seed=0)
    with pytest.raises(ValueError, match="p_env"):
        PromisedCycle(length=100, period=4, alphabet=4, p_env=1.5, seed=0)


# --------------------------------------------------------------------- #
# .simple() factory (since v0.8.2a0)
# --------------------------------------------------------------------- #


def test_simple_factory_returns_promised_cycle_instance() -> None:
    sys = PromisedCycle.simple()
    assert isinstance(sys, PromisedCycle)


def test_simple_factory_defaults_clear_memory_minimum() -> None:
    """The default ``length`` must clear the 500-timestep memory floor."""
    sys = PromisedCycle.simple()
    assert sys.length >= 500


def test_simple_factory_default_p_noise_is_low_but_nonzero() -> None:
    sys = PromisedCycle.simple()
    assert 0.0 < sys.p_noise < 0.5


def test_simple_factory_picks_consistent_period_and_alphabet() -> None:
    """Default ``period == alphabet`` so the cycle visits every symbol."""
    sys = PromisedCycle.simple()
    assert sys.period == sys.alphabet


def test_simple_factory_accepts_p_noise_override() -> None:
    sys = PromisedCycle.simple(p_noise=0.4)
    assert sys.p_noise == pytest.approx(0.4)


def test_simple_factory_accepts_seed_override() -> None:
    sys_a = PromisedCycle.simple(seed=1)
    sys_b = PromisedCycle.simple(seed=2)
    declared_a, _ = sys_a.get_declared_executed()
    declared_b, _ = sys_b.get_declared_executed()
    # Same length, same period, same alphabet, but different env-noise stream
    # produces different executed channels even at p_noise=0.1.
    _, executed_a = sys_a.get_declared_executed()
    _, executed_b = sys_b.get_declared_executed()
    assert not np.array_equal(executed_a, executed_b)


def test_simple_factory_end_to_end_with_measure() -> None:
    """Smoke test mirroring the canonical README cookbook entry."""
    import autonometrics as anm

    sys = PromisedCycle.simple()
    profile = anm.measure(sys)
    assert profile.closure is not None
    assert profile.memory is not None
    assert profile.persistence is not None
    assert profile.coherence is not None
