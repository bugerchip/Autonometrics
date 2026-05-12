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


# --------------------------------------------------------------------- #
# .demo() factory (since v0.8.2a0)
# --------------------------------------------------------------------- #


def test_demo_factory_returns_self_generated_by_default() -> None:
    sys = SimpleAutomaton.demo()
    assert sys.mode == "self_generated"


def test_demo_factory_external_mode_works() -> None:
    sys = SimpleAutomaton.demo(mode="external")
    assert sys.mode == "external"


def test_demo_factory_default_env_has_expected_length() -> None:
    sys = SimpleAutomaton.demo()
    assert sys.get_env_history().shape == (3000,)


def test_demo_factory_custom_n_steps_propagates() -> None:
    sys = SimpleAutomaton.demo(n_steps=500)
    assert sys.get_env_history().shape == (500,)


def test_demo_factory_custom_n_states_bounds_state_history() -> None:
    sys = SimpleAutomaton.demo(n_states=6)
    states = sys.get_state_history()
    assert states.min() >= 0
    assert states.max() < 6


def test_demo_factory_seed_is_reproducible() -> None:
    sys_a = SimpleAutomaton.demo(seed=7)
    sys_b = SimpleAutomaton.demo(seed=7)
    np.testing.assert_array_equal(sys_a.get_env_history(), sys_b.get_env_history())
    np.testing.assert_array_equal(sys_a.get_state_history(), sys_b.get_state_history())


def test_demo_factory_different_seeds_diverge() -> None:
    sys_a = SimpleAutomaton.demo(seed=1)
    sys_b = SimpleAutomaton.demo(seed=2)
    assert not np.array_equal(sys_a.get_env_history(), sys_b.get_env_history())


def test_demo_factory_rejects_unknown_mode() -> None:
    with pytest.raises(ValueError, match="Unknown mode"):
        SimpleAutomaton.demo(mode="nonsense")


def test_demo_factory_end_to_end_with_measure() -> None:
    """Smoke test mirroring the canonical README cookbook entry."""
    import autonometrics as anm

    sys_self = SimpleAutomaton.demo(mode="self_generated")
    profile_self = anm.measure(sys_self, axes=["closure", "memory"])
    assert profile_self.closure is not None
    assert profile_self.memory is not None

    sys_ext = SimpleAutomaton.demo(mode="external")
    profile_ext = anm.measure(sys_ext, axes=["closure", "memory"])
    assert profile_ext.closure is not None
    assert profile_ext.memory is not None
    # Sanity: the self-generated automaton scores higher on closure
    # than the externally-driven one (the qualitative claim that
    # motivates the demo in the first place).
    assert profile_self.closure > profile_ext.closure
