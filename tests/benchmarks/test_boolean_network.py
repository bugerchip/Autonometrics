"""Tests for the KauffmanNetwork benchmark adapter."""

import numpy as np
import pytest

from autonometrics import Autonometer
from autonometrics.benchmarks import KauffmanNetwork


def test_history_shapes_and_dtypes() -> None:
    net = KauffmanNetwork(n_nodes=10, k=3, n_steps=600, seed=0)
    states = net.get_state_history()
    env = net.get_env_history()

    assert states.shape == (600,)
    assert env.shape == (600,)
    assert states.dtype == np.int64
    assert env.dtype == np.int64


def test_states_are_binary() -> None:
    net = KauffmanNetwork(n_nodes=8, k=3, n_steps=600, seed=1)
    states = net.get_state_history()
    env = net.get_env_history()
    assert set(np.unique(states).tolist()) <= {0, 1}
    assert set(np.unique(env).tolist()) <= {0, 1}


def test_reproducible_with_same_seed() -> None:
    a = KauffmanNetwork(n_nodes=8, k=3, n_steps=300, coupling=0.5, seed=42).get_state_history()
    b = KauffmanNetwork(n_nodes=8, k=3, n_steps=300, coupling=0.5, seed=42).get_state_history()
    np.testing.assert_array_equal(a, b)


def test_different_seed_yields_different_history() -> None:
    a = KauffmanNetwork(n_nodes=8, k=3, n_steps=300, coupling=0.5, seed=1).get_state_history()
    b = KauffmanNetwork(n_nodes=8, k=3, n_steps=300, coupling=0.5, seed=2).get_state_history()
    assert not np.array_equal(a, b)


def test_zero_coupling_makes_focal_self_dependent() -> None:
    """With ``coupling=0`` the focal node's next state is a function of its own past only.

    Random truth tables routinely collapse the focal trajectory to a
    constant after a short transient; in that case ``H(S_{t+1} | E_t) = 0``
    and Albantakis correctly raises. Among non-degenerate seeds (period
    >= 2 focal trajectory), closure must saturate near ``1``.
    """
    saw_non_degenerate = False
    for seed in range(50):
        net = KauffmanNetwork(n_nodes=10, k=3, n_steps=2000, coupling=0.0, seed=seed)
        states = net.get_state_history()
        if np.unique(states[500:]).size >= 2:
            profile = Autonometer(metrics=["albantakis"]).measure(net)
            assert profile.ratio_endo_total is not None
            assert profile.ratio_endo_total >= 0.95
            saw_non_degenerate = True
            break
    assert saw_non_degenerate, "no non-degenerate focal trajectory found in 50 seeds"


def test_full_coupling_makes_focal_externally_driven() -> None:
    """With ``coupling=1`` the focal node has no self-input."""
    net = KauffmanNetwork(n_nodes=10, k=3, n_steps=2000, coupling=1.0, seed=0)
    states = net.get_state_history()
    assert states.size == 2000


def test_get_state_history_returns_copy() -> None:
    net = KauffmanNetwork(n_nodes=8, k=3, n_steps=300, seed=0)
    out = net.get_state_history()
    out[0] = -999
    assert net.get_state_history()[0] in (0, 1)


def test_smoke_with_autonometer_full_profile() -> None:
    net = KauffmanNetwork(n_nodes=10, k=3, n_steps=2000, coupling=0.5, seed=0)
    profile = Autonometer(metrics=["albantakis", "memory"]).measure(net)
    if profile.ratio_endo_total is not None:
        assert 0.0 <= profile.ratio_endo_total <= 1.0
    assert profile.memory_endo_ratio is not None
    assert 0.0 <= profile.memory_endo_ratio <= 1.0


def test_rejects_invalid_n_nodes() -> None:
    with pytest.raises(ValueError, match="n_nodes"):
        KauffmanNetwork(n_nodes=2, k=2, n_steps=100)


def test_rejects_k_exceeding_n_nodes() -> None:
    with pytest.raises(ValueError, match="cannot exceed"):
        KauffmanNetwork(n_nodes=4, k=10, n_steps=100)


def test_rejects_invalid_coupling() -> None:
    with pytest.raises(ValueError, match="coupling"):
        KauffmanNetwork(n_nodes=5, k=2, n_steps=100, coupling=1.5)
    with pytest.raises(ValueError, match="coupling"):
        KauffmanNetwork(n_nodes=5, k=2, n_steps=100, coupling=-0.1)


def test_rejects_invalid_n_steps() -> None:
    with pytest.raises(ValueError, match="n_steps"):
        KauffmanNetwork(n_nodes=5, k=2, n_steps=1)
