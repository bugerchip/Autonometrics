"""Tests for the SimpleAutomaton adapter."""

import numpy as np
import pytest

from autonometrics import SimpleAutomaton


def _make_env(seed: int = 0, n_steps: int = 1000, n_symbols: int = 3) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, n_symbols, size=n_steps).astype(np.int64)


def test_self_generated_history_has_expected_shape() -> None:
    env = _make_env()
    a = SimpleAutomaton.from_self_generated_rules(n_states=4, env=env, seed=0)
    states = a.get_state_history()
    assert states.shape == env.shape
    assert states.dtype == np.int64
    assert states.min() >= 0
    assert states.max() < 4


def test_external_history_has_expected_shape() -> None:
    env = _make_env()
    b = SimpleAutomaton.from_external_rules(n_states=4, env=env, seed=0)
    states = b.get_state_history()
    assert states.shape == env.shape
    assert states.dtype == np.int64


def test_self_generated_is_reproducible() -> None:
    env = _make_env()
    a1 = SimpleAutomaton.from_self_generated_rules(n_states=5, env=env, seed=42)
    a2 = SimpleAutomaton.from_self_generated_rules(n_states=5, env=env, seed=42)
    np.testing.assert_array_equal(a1.get_state_history(), a2.get_state_history())


def test_external_is_reproducible() -> None:
    env = _make_env()
    b1 = SimpleAutomaton.from_external_rules(n_states=5, env=env, seed=42)
    b2 = SimpleAutomaton.from_external_rules(n_states=5, env=env, seed=42)
    np.testing.assert_array_equal(b1.get_state_history(), b2.get_state_history())


def test_self_generated_ignores_env_content() -> None:
    env_a = _make_env(seed=1)
    env_b = _make_env(seed=2)
    a = SimpleAutomaton.from_self_generated_rules(n_states=4, env=env_a, seed=0)
    b = SimpleAutomaton.from_self_generated_rules(n_states=4, env=env_b, seed=0)
    np.testing.assert_array_equal(a.get_state_history(), b.get_state_history())


def test_get_env_history_returns_copy() -> None:
    env = _make_env()
    a = SimpleAutomaton.from_self_generated_rules(n_states=4, env=env, seed=0)
    returned = a.get_env_history()
    returned[0] = -999
    np.testing.assert_array_equal(a.get_env_history(), env)


def test_rejects_too_few_states() -> None:
    env = _make_env()
    with pytest.raises(ValueError, match="n_states"):
        SimpleAutomaton.from_self_generated_rules(n_states=1, env=env, seed=0)


def test_rejects_too_short_env() -> None:
    with pytest.raises(ValueError, match="at least 2 timesteps"):
        SimpleAutomaton.from_self_generated_rules(n_states=3, env=np.array([0]), seed=0)


def test_rejects_noise_out_of_range() -> None:
    env = _make_env()
    with pytest.raises(ValueError, match="external_noise"):
        SimpleAutomaton.from_external_rules(n_states=3, env=env, seed=0, noise=1.5)


def test_mode_property() -> None:
    env = _make_env()
    a = SimpleAutomaton.from_self_generated_rules(n_states=3, env=env, seed=0)
    b = SimpleAutomaton.from_external_rules(n_states=3, env=env, seed=0)
    assert a.mode == "self_generated"
    assert b.mode == "external"
