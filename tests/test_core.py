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


def test_default_metric_is_all_five_axes() -> None:
    """Since v0.8.1a0, ``Autonometer()`` defaults to all five axes.

    The legacy default of ``["albantakis"]`` only — kept from v0.1.x —
    silently dropped four of the five canonical readings, which made
    the orchestrator surprising for new users. The default now matches
    the canonical public surface (``AXES``), keeping the mosaic-dropout
    policy (axes the adapter does not support are reported as ``None``).
    """
    meter = Autonometer()
    assert meter.metrics == [
        "albantakis",
        "memory",
        "constraint_closure",
        "persistence",
        "coherence",
    ]
    assert meter.metric == "albantakis"  # property still returns first entry


def test_explicit_single_metric_backward_compat() -> None:
    meter = Autonometer(metric="memory")
    assert meter.metrics == ["memory"]
    assert meter.metric == "memory"


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
    assert profile.memory_endo_ratio is None


def test_memory_only_leaves_ratio_endo_total_none() -> None:
    system = _make_system()
    profile = Autonometer(metrics=["memory"]).measure(system)

    assert profile.ratio_endo_total is None
    assert profile.memory_endo_ratio is not None
    assert 0.0 <= profile.memory_endo_ratio <= 1.0


def test_multi_metric_populates_both_fields() -> None:
    system = _make_system()
    profile = Autonometer(metrics=["albantakis", "memory"]).measure(system)

    assert profile.ratio_endo_total is not None
    assert profile.memory_endo_ratio is not None
    assert profile.metadata["metrics"] == ["albantakis", "memory"]


def test_metadata_is_populated() -> None:
    system = _make_system(n=1500)
    profile = Autonometer().measure(system)

    assert profile.metadata["metric"] == "albantakis"
    assert profile.metadata["metrics"] == [
        "albantakis",
        "memory",
        "constraint_closure",
        "persistence",
        "coherence",
    ]
    assert profile.metadata["axes"] == [
        "closure",
        "memory",
        "constraint",
        "persistence",
        "coherence",
    ]
    assert profile.metadata["n_timesteps"] == 1500
    assert profile.metadata["adapter"] == "_StaticSystem"


def test_persistence_returns_none_when_adapter_lacks_replay() -> None:
    """``CSVTrajectory``-style replay-less adapters must score ``None``
    on the persistence axis without aborting other axes.
    """
    system = _make_system(n=1500)
    profile = Autonometer(metrics=["persistence"]).measure(system)
    assert profile.rai_proxy_persistence is None
    assert profile.ratio_endo_total is None
    assert profile.memory_endo_ratio is None
    assert profile.constraint_closure is None


def test_persistence_runs_when_adapter_exposes_replay() -> None:
    from autonometrics.benchmarks import ECASystem

    eca = ECASystem(rule=110, n_steps=400, width=51, seed=0)
    profile = Autonometer(metrics=["persistence"]).measure(eca)
    assert profile.rai_proxy_persistence is not None
    assert 0.0 <= profile.rai_proxy_persistence <= 1.0


def test_four_axis_combo_populates_only_requested_fields() -> None:
    from autonometrics.benchmarks import ECASystem

    eca = ECASystem(rule=110, n_steps=600, width=51, seed=0)
    profile = Autonometer(
        metrics=["albantakis", "memory", "constraint_closure", "persistence"]
    ).measure(eca)
    assert profile.ratio_endo_total is not None
    assert profile.memory_endo_ratio is not None
    assert profile.constraint_closure is not None
    assert profile.rai_proxy_persistence is not None
    assert profile.metadata["metrics"] == [
        "albantakis",
        "memory",
        "constraint_closure",
        "persistence",
    ]
