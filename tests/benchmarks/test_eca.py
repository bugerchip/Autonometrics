"""Tests for the ECASystem benchmark adapter."""

import numpy as np
import pytest

from autonometrics import Autonometer
from autonometrics.benchmarks import ECASystem


def test_history_shapes_and_dtypes() -> None:
    eca = ECASystem(rule=110, n_steps=600, width=51, seed=0)
    states = eca.get_state_history()
    env = eca.get_env_history()

    assert states.shape == (600,)
    assert env.shape == (600,)
    assert states.dtype == np.int64
    assert env.dtype == np.int64


def test_state_alphabet_is_binary() -> None:
    eca = ECASystem(rule=30, n_steps=600, width=51, seed=1)
    states = eca.get_state_history()
    assert set(np.unique(states).tolist()) <= {0, 1}


def test_env_alphabet_is_four() -> None:
    eca = ECASystem(rule=110, n_steps=600, width=51, seed=2)
    env = eca.get_env_history()
    unique = set(np.unique(env).tolist())
    assert unique <= {0, 1, 2, 3}


def test_reproducible_with_same_seed() -> None:
    a = ECASystem(rule=30, n_steps=300, width=51, seed=42).get_state_history()
    b = ECASystem(rule=30, n_steps=300, width=51, seed=42).get_state_history()
    np.testing.assert_array_equal(a, b)


def test_different_seed_yields_different_history() -> None:
    a = ECASystem(rule=30, n_steps=300, width=51, seed=1).get_state_history()
    b = ECASystem(rule=30, n_steps=300, width=51, seed=2).get_state_history()
    assert not np.array_equal(a, b)


def test_get_state_history_returns_copy() -> None:
    eca = ECASystem(rule=110, n_steps=300, width=51, seed=0)
    out = eca.get_state_history()
    out[0] = -999
    assert eca.get_state_history()[0] in (0, 1)


def test_single_init_starts_with_lone_centre_cell() -> None:
    eca = ECASystem(rule=110, n_steps=2, width=11, seed=0, init="single")
    states = eca.get_state_history()
    assert states[0] == 1


def test_rule_zero_decays_to_constant() -> None:
    eca = ECASystem(rule=0, n_steps=300, width=51, seed=0)
    states = eca.get_state_history()
    assert (states[1:] == 0).all()


def test_rule_255_drives_to_constant_one() -> None:
    eca = ECASystem(rule=255, n_steps=300, width=51, seed=0)
    states = eca.get_state_history()
    assert (states[1:] == 1).all()


def test_smoke_with_autonometer_albantakis() -> None:
    eca = ECASystem(rule=110, n_steps=600, width=51, seed=0)
    profile = Autonometer(metrics=["albantakis"]).measure(eca)
    assert profile.ratio_endo_total is not None
    assert 0.0 <= profile.ratio_endo_total <= 1.0


def test_smoke_with_autonometer_memory() -> None:
    eca = ECASystem(rule=110, n_steps=2000, width=51, seed=0)
    profile = Autonometer(metrics=["memory"]).measure(eca)
    assert profile.memory_endo_ratio is not None
    assert 0.0 <= profile.memory_endo_ratio <= 1.0


def test_rejects_invalid_rule() -> None:
    with pytest.raises(ValueError, match="rule"):
        ECASystem(rule=300, n_steps=100)
    with pytest.raises(ValueError, match="rule"):
        ECASystem(rule=-1, n_steps=100)


def test_rejects_invalid_width() -> None:
    with pytest.raises(ValueError, match="width"):
        ECASystem(rule=110, n_steps=100, width=3)


def test_rejects_invalid_n_steps() -> None:
    with pytest.raises(ValueError, match="n_steps"):
        ECASystem(rule=110, n_steps=1)


def test_rejects_invalid_init() -> None:
    with pytest.raises(ValueError, match="init"):
        ECASystem(rule=110, n_steps=100, init="bogus")
