"""Unit tests for ``compute_rai_proxy_persistence``."""

from __future__ import annotations

import numpy as np
import pytest

from autonometrics.metrics import compute_rai_proxy_persistence


def _identity_replay(states: np.ndarray):
    """Build a replay_fn that returns the unperturbed continuation.

    A perfect-persistence system: every replay equals the baseline,
    so ``d_bar = 0`` and the score is ``1.0``.
    """

    def replay(t_star: int, n_steps: int, rng=None) -> np.ndarray:
        return states[t_star + 1 : t_star + 1 + n_steps].copy()

    return replay


def _independent_replay(rng_seed: int, alphabet: int, length: int):
    """Return replay_fn that always emits a fresh independent sample.

    A no-persistence system: replay is statistically independent of
    the baseline trajectory, so ``d_bar`` approaches ``d_ref`` and
    the score collapses toward ``0``.
    """
    del rng_seed  # reserved for future re-seeding; inner replay uses its own rng

    def replay(t_star: int, n_steps: int, rng=None) -> np.ndarray:
        del t_star
        return rng_inner_sample(rng_inner=rng, draws=n_steps, alphabet=alphabet)

    def rng_inner_sample(rng_inner, draws: int, alphabet: int) -> np.ndarray:
        gen = rng_inner if rng_inner is not None else np.random.default_rng(0)
        return gen.integers(0, alphabet, size=draws).astype(np.int64)

    return replay


def test_perfect_replay_returns_one() -> None:
    rng = np.random.default_rng(0)
    states = rng.integers(0, 2, size=200).astype(np.int64)
    env = rng.integers(0, 2, size=200).astype(np.int64)
    score = compute_rai_proxy_persistence(
        states,
        env,
        _identity_replay(states),
        n_perturbations=8,
        horizon=32,
    )
    assert score == pytest.approx(1.0)


def test_independent_replay_drives_score_low() -> None:
    rng = np.random.default_rng(1)
    states = rng.integers(0, 2, size=400).astype(np.int64)
    env = rng.integers(0, 2, size=400).astype(np.int64)

    def replay(t_star: int, n_steps: int, rng=None) -> np.ndarray:
        gen = rng if rng is not None else np.random.default_rng(0)
        return gen.integers(0, 2, size=n_steps).astype(np.int64)

    score = compute_rai_proxy_persistence(
        states,
        env,
        replay,
        n_perturbations=64,
        horizon=64,
        rng=np.random.default_rng(2),
    )
    # Two independent fair coins → d_bar ≈ d_ref ≈ 0.5; score ≈ 0
    assert 0.0 <= score <= 0.15


def test_constant_trajectory_raises() -> None:
    states = np.zeros(200, dtype=np.int64)
    env = np.zeros(200, dtype=np.int64)
    with pytest.raises(ValueError, match="constant"):
        compute_rai_proxy_persistence(states, env, _identity_replay(states))


def test_short_trajectory_raises() -> None:
    states = np.array([0, 1, 0, 1], dtype=np.int64)
    env = np.zeros_like(states)
    with pytest.raises(ValueError, match="too short"):
        compute_rai_proxy_persistence(states, env, _identity_replay(states), horizon=64)


def test_mismatched_lengths_raises() -> None:
    states = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1], dtype=np.int64)
    env = np.array([0, 1, 0], dtype=np.int64)
    with pytest.raises(ValueError, match="same length"):
        compute_rai_proxy_persistence(states, env, _identity_replay(states))


def test_non_integer_states_raises() -> None:
    states = np.linspace(0.0, 1.0, num=200)
    env = np.zeros(200, dtype=np.int64)
    with pytest.raises(ValueError, match="integer"):
        compute_rai_proxy_persistence(states, env, _identity_replay(states))


def test_replay_returning_wrong_length_raises() -> None:
    rng = np.random.default_rng(3)
    states = rng.integers(0, 2, size=200).astype(np.int64)
    env = rng.integers(0, 2, size=200).astype(np.int64)

    def bad_replay(t_star: int, n_steps: int, rng=None) -> np.ndarray:
        return np.zeros(n_steps - 1, dtype=np.int64)

    with pytest.raises(ValueError, match="replay_fn returned"):
        compute_rai_proxy_persistence(
            states,
            env,
            bad_replay,
            n_perturbations=2,
            horizon=10,
        )


def test_partial_recovery_yields_intermediate_score() -> None:
    """A replay that mostly matches but occasionally flips lands in (0, 1)."""
    rng = np.random.default_rng(4)
    states = rng.integers(0, 2, size=500).astype(np.int64)
    env = rng.integers(0, 2, size=500).astype(np.int64)
    flip_rng = np.random.default_rng(5)

    def replay(t_star: int, n_steps: int, rng=None) -> np.ndarray:
        baseline = states[t_star + 1 : t_star + 1 + n_steps].copy()
        flips = flip_rng.random(n_steps) < 0.30
        return np.where(flips, 1 - baseline, baseline).astype(np.int64)

    score = compute_rai_proxy_persistence(
        states,
        env,
        replay,
        n_perturbations=32,
        horizon=64,
        rng=np.random.default_rng(6),
    )
    assert 0.20 <= score <= 0.55


def test_d_ref_uses_marginal_collision_complement() -> None:
    """Skewed marginals shrink d_ref and rescale the score correctly.

    A 90/10 binary trajectory has ``d_ref ≈ 0.18``. An independent
    fair replay (mismatch ≈ 0.5 against this baseline) should still
    drive the score below ``d_ref`` calibration: ``1 - d_bar/d_ref``
    is negative, which clips to ``0``. We check the clipping path.
    """
    rng = np.random.default_rng(7)
    skewed = rng.choice([0, 1], size=500, p=[0.9, 0.1]).astype(np.int64)
    env = np.zeros_like(skewed)

    def replay(t_star: int, n_steps: int, rng=None) -> np.ndarray:
        gen = rng if rng is not None else np.random.default_rng(8)
        return gen.integers(0, 2, size=n_steps).astype(np.int64)

    score = compute_rai_proxy_persistence(
        skewed,
        env,
        replay,
        n_perturbations=32,
        horizon=64,
        rng=np.random.default_rng(9),
    )
    assert score == pytest.approx(0.0, abs=1e-9)


def test_persistence_does_not_import_other_metrics() -> None:
    """Audit: the module is information-theory-free and graph-free."""
    import autonometrics.metrics.persistence as mod

    src = open(mod.__file__, encoding="utf-8").read()
    assert "from autonometrics.metrics._entropy" not in src
    assert "import autonometrics.metrics._entropy" not in src
    assert "from autonometrics.metrics.albantakis" not in src
    assert "from autonometrics.metrics.memory_ratio" not in src
    assert "from autonometrics.metrics.constraint_closure" not in src
    assert "import pyinform" not in src
    assert "import dit" not in src
