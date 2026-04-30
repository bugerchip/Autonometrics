"""Tests for the Autonometer orchestrator."""

import numpy as np
import pytest

from autonometrics import Autonometer, AutonomyProfile


class _StaticSystem:
    def __init__(self, states: np.ndarray, env: np.ndarray) -> None:
        self._states = states
        self._env = env

    def get_state_history(self) -> np.ndarray:
        return self._states

    def get_env_history(self) -> np.ndarray:
        return self._env


def test_default_metric_is_albantakis() -> None:
    meter = Autonometer()
    assert meter.metric == "albantakis"


def test_unknown_metric_raises() -> None:
    with pytest.raises(ValueError, match="Unknown metric"):
        Autonometer(metric="does-not-exist")


def test_measure_rejects_non_system() -> None:
    meter = Autonometer()
    with pytest.raises(TypeError, match="AutonomySystem protocol"):
        meter.measure(object())


def test_measure_returns_profile() -> None:
    rng = np.random.default_rng(0)
    states = np.arange(64) % 4
    env = rng.integers(0, 3, size=64)

    system = _StaticSystem(states=states, env=env)
    profile = Autonometer().measure(system)

    assert isinstance(profile, AutonomyProfile)
    assert 0.0 <= profile.ratio_endo_total <= 1.0
    assert profile.metadata["metric"] == "albantakis"
    assert profile.metadata["n_timesteps"] == 64
    assert profile.metadata["adapter"] == "_StaticSystem"
