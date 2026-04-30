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


def _make_system(seed: int = 0, n: int = 1500) -> _StaticSystem:
    rng = np.random.default_rng(seed)
    states = np.arange(n) % 4
    env = rng.integers(0, 3, size=n)
    return _StaticSystem(states=states, env=env)


def test_default_metric_is_albantakis() -> None:
    meter = Autonometer()
    assert meter.metrics == ["albantakis"]
    assert meter.metric == "albantakis"


def test_explicit_single_metric_backward_compat() -> None:
    meter = Autonometer(metric="autopoietic")
    assert meter.metrics == ["autopoietic"]
    assert meter.metric == "autopoietic"


def test_unknown_metric_raises() -> None:
    with pytest.raises(ValueError, match="Unknown metric"):
        Autonometer(metric="does-not-exist")


def test_unknown_metric_in_list_raises() -> None:
    with pytest.raises(ValueError, match="Unknown metric"):
        Autonometer(metrics=["albantakis", "bogus"])


def test_empty_metrics_list_raises() -> None:
    with pytest.raises(ValueError, match="at least one metric"):
        Autonometer(metrics=[])


def test_measure_rejects_non_system() -> None:
    meter = Autonometer()
    with pytest.raises(TypeError, match="AutonomySystem protocol"):
        meter.measure(object())


def test_single_metric_populates_only_its_field() -> None:
    system = _make_system()
    profile = Autonometer(metrics=["albantakis"]).measure(system)

    assert isinstance(profile, AutonomyProfile)
    assert profile.ratio_endo_total is not None
    assert 0.0 <= profile.ratio_endo_total <= 1.0
    assert profile.autopoietic_ratio is None


def test_autopoietic_only_leaves_ratio_endo_total_none() -> None:
    system = _make_system()
    profile = Autonometer(metrics=["autopoietic"]).measure(system)

    assert profile.ratio_endo_total is None
    assert profile.autopoietic_ratio is not None
    assert profile.autopoietic_ratio >= 0.0


def test_multi_metric_populates_both_fields() -> None:
    system = _make_system()
    profile = Autonometer(metrics=["albantakis", "autopoietic"]).measure(system)

    assert profile.ratio_endo_total is not None
    assert profile.autopoietic_ratio is not None
    assert profile.metadata["metrics"] == ["albantakis", "autopoietic"]


def test_metadata_is_populated() -> None:
    system = _make_system(n=1500)
    profile = Autonometer().measure(system)

    assert profile.metadata["metric"] == "albantakis"
    assert profile.metadata["metrics"] == ["albantakis"]
    assert profile.metadata["n_timesteps"] == 1500
    assert profile.metadata["adapter"] == "_StaticSystem"
