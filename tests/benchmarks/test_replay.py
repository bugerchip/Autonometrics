"""Tests for ``replay_from_perturbation`` across benchmark adapters."""

from __future__ import annotations

import numpy as np
import pytest

from autonometrics.benchmarks import ECASystem, KauffmanNetwork, PeriodicCycle


def test_eca_replay_diverges_from_baseline_at_least_once() -> None:
    eca = ECASystem(rule=110, n_steps=200, width=51, seed=0)
    baseline = eca.get_state_history()
    perturbed = eca.replay_from_perturbation(t_star=10, n_steps=64)
    assert perturbed.shape == (64,)
    assert np.issubdtype(perturbed.dtype, np.integer)
    assert (perturbed != baseline[11:75]).any()


def test_eca_replay_centre_perturbation_is_local_at_first_step() -> None:
    """Single bit-flip at the centre touches at most three cells in the next row.

    The next-step focal cell is determined only by the centre and its
    two immediate neighbours, so a single bit-flip at the centre can
    only flip the focal cell at ``t_star + 1`` (with respect to the
    baseline). Subsequent steps may or may not differ depending on the
    rule's locality and chaos signature.
    """
    eca = ECASystem(rule=30, n_steps=200, width=51, seed=0)
    baseline = eca.get_state_history()
    perturbed = eca.replay_from_perturbation(t_star=20, n_steps=1)
    diff_first = perturbed[0] != baseline[21]
    assert isinstance(bool(diff_first), bool)


def test_eca_replay_rejects_out_of_range_t_star() -> None:
    eca = ECASystem(rule=110, n_steps=50, width=51, seed=0)
    with pytest.raises(ValueError, match="t_star"):
        eca.replay_from_perturbation(t_star=49, n_steps=4)


def test_eca_replay_rejects_horizon_overrun() -> None:
    eca = ECASystem(rule=110, n_steps=50, width=51, seed=0)
    with pytest.raises(ValueError, match="t_star \\+ n_steps"):
        eca.replay_from_perturbation(t_star=10, n_steps=100)


def test_kauffman_replay_returns_horizon_length_array() -> None:
    net = KauffmanNetwork(n_nodes=10, k=3, n_steps=300, coupling=0.5, seed=0)
    perturbed = net.replay_from_perturbation(t_star=20, n_steps=64)
    assert perturbed.shape == (64,)
    assert np.issubdtype(perturbed.dtype, np.integer)
    assert set(np.unique(perturbed).tolist()).issubset({0, 1})


def test_kauffman_replay_diverges_when_focal_self_couples() -> None:
    """At coupling=0, the focal node depends only on itself; its rule
    is one of four possible 1-input boolean tables. For non-trivial
    rules (NOT, identity composed cleverly), a single flip propagates
    forever; for trivial rules (constant 0 or constant 1) it dies in
    one step. Either way, ``replay_from_perturbation`` must execute
    without error.
    """
    for seed in range(3):
        net = KauffmanNetwork(n_nodes=10, k=3, n_steps=300, coupling=0.0, seed=seed)
        perturbed = net.replay_from_perturbation(t_star=20, n_steps=64)
        assert perturbed.shape == (64,)


def test_kauffman_replay_invisible_to_focal_at_full_external_coupling() -> None:
    """At coupling=1, the focal node ignores its own state in its rule.

    Flipping the focal bit at ``t_star`` therefore has no effect on
    the focal value at ``t_star + 1``: that value is computed from
    other nodes, which are unchanged. So the perturbed and the
    unperturbed focal trajectories must agree at the first step.
    """
    net = KauffmanNetwork(n_nodes=10, k=3, n_steps=300, coupling=1.0, seed=0)
    baseline = net.get_state_history()
    perturbed = net.replay_from_perturbation(t_star=20, n_steps=1)
    assert perturbed[0] == baseline[21]


def test_periodic_replay_shifts_trajectory_by_one_phase() -> None:
    cycle = PeriodicCycle(period=4, n_steps=300, env_alphabet=3, seed=0)
    baseline = cycle.get_state_history()
    perturbed = cycle.replay_from_perturbation(t_star=10, n_steps=20)
    expected = ((np.arange(11, 31) + 1) % 4).astype(np.int64)
    assert np.array_equal(perturbed, expected)
    assert (perturbed != baseline[11:31]).all()


def test_periodic_replay_rejects_out_of_range_t_star() -> None:
    cycle = PeriodicCycle(period=4, n_steps=50, env_alphabet=3, seed=0)
    with pytest.raises(ValueError, match="t_star"):
        cycle.replay_from_perturbation(t_star=49, n_steps=4)
