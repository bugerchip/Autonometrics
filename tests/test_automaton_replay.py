"""Tests for :class:`SimpleAutomaton.replay_from_perturbation`."""

from __future__ import annotations

import numpy as np
import pytest

from autonometrics import SimpleAutomaton


def _env(n: int = 200, alphabet: int = 3, seed: int = 0) -> np.ndarray:
    return (
        np.random.default_rng(seed)
        .integers(0, alphabet, size=n)
        .astype(np.int64)
    )


def test_self_generated_replay_shifts_trajectory_by_one_orbit_step() -> None:
    aut = SimpleAutomaton.from_self_generated_rules(
        n_states=4, env=_env(n=200, seed=1), seed=2
    )
    baseline = aut.get_state_history()
    perturbed = aut.replay_from_perturbation(t_star=20, n_steps=10)
    assert perturbed.shape == (10,)
    assert (perturbed != baseline[21:31]).all()


def test_self_generated_replay_stays_inside_alphabet() -> None:
    aut = SimpleAutomaton.from_self_generated_rules(
        n_states=4, env=_env(n=200, seed=3), seed=4
    )
    perturbed = aut.replay_from_perturbation(t_star=10, n_steps=64)
    assert set(np.unique(perturbed).tolist()).issubset({0, 1, 2, 3})


def test_external_replay_shares_noise_plan_with_baseline() -> None:
    """Re-using the cached noise plan means the only divergence comes
    from the perturbed initial state propagating through the env-table
    branch of the rule. Steps that happened to be noise events in the
    original run remain noise events with the *same* replacement value
    in the replay."""
    aut = SimpleAutomaton.from_external_rules(
        n_states=3, env=_env(n=300, seed=5), seed=6, noise=0.20
    )
    baseline = aut.get_state_history()
    perturbed = aut.replay_from_perturbation(t_star=30, n_steps=20)

    assert perturbed.shape == (20,)
    assert set(np.unique(perturbed).tolist()).issubset({0, 1, 2})
    # The perturbation only affects the value at t_star itself; from
    # t_star+1 onwards the rule does not depend on the previous state
    # in external mode (it depends on env or on a cached noise draw).
    # Therefore the perturbed continuation must equal the baseline
    # continuation step-by-step.
    np.testing.assert_array_equal(perturbed, baseline[31:51])


def test_replay_rejects_out_of_range_t_star() -> None:
    aut = SimpleAutomaton.from_self_generated_rules(
        n_states=3, env=_env(n=50, seed=7), seed=8
    )
    with pytest.raises(ValueError, match="t_star"):
        aut.replay_from_perturbation(t_star=49, n_steps=4)


def test_replay_rejects_horizon_overrun() -> None:
    aut = SimpleAutomaton.from_self_generated_rules(
        n_states=3, env=_env(n=50, seed=9), seed=10
    )
    with pytest.raises(ValueError, match="t_star \\+ n_steps"):
        aut.replay_from_perturbation(t_star=10, n_steps=100)
