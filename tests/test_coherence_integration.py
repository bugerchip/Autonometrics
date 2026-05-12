"""End-to-end integration tests for the CBA (coherence) axis.

Verifies the orchestrator wiring: ``Autonometer(metrics=["coherence"])``
produces a populated ``AutonomyProfile.cba_theil_u`` on adapters that
expose ``get_declared_executed`` and ``None`` on adapters that do not.
"""

from __future__ import annotations

import numpy as np
import pytest

from autonometrics import (
    Autonometer,
    AutonomyProfile,
    PromisedCycle,
    SimpleAutomaton,
)


def test_autonometer_measures_cba_on_promised_cycle_zero_noise() -> None:
    sys = PromisedCycle(length=512, period=4, alphabet=4, p_noise=0.0, seed=0)
    profile = Autonometer(metrics=["coherence"]).measure(sys)
    assert isinstance(profile, AutonomyProfile)
    assert profile.cba_theil_u is not None
    assert profile.cba_theil_u >= 0.95


def test_autonometer_measures_cba_on_promised_cycle_full_noise() -> None:
    sys = PromisedCycle(length=2000, period=4, alphabet=4, p_noise=1.0, seed=0)
    profile = Autonometer(metrics=["coherence"]).measure(sys)
    assert profile.cba_theil_u is not None
    assert profile.cba_theil_u <= 0.10


def test_autonometer_handles_adversarial_shift() -> None:
    sys = PromisedCycle(
        length=512,
        period=4,
        alphabet=5,
        mode="adversarial_shift",
        seed=0,
    )
    profile = Autonometer(metrics=["coherence"]).measure(sys)
    assert profile.cba_theil_u is not None
    assert profile.cba_theil_u >= 0.90


def test_autonometer_returns_none_cba_on_simple_automaton() -> None:
    """Adapters without a declarative layer drop out of CBA cleanly."""
    rng = np.random.default_rng(0)
    env = rng.integers(0, 3, size=300).astype(np.int64)
    sys = SimpleAutomaton.from_self_generated_rules(n_states=3, env=env, seed=0)
    profile = Autonometer(metrics=["coherence"]).measure(sys)
    assert profile.cba_theil_u is None


def test_five_axis_profile_on_promised_cycle() -> None:
    """Running all five axes on PromisedCycle returns five floats (no crashes)."""
    sys = PromisedCycle(length=512, period=4, alphabet=4, p_noise=0.2, seed=0)
    meter = Autonometer(
        metrics=["albantakis", "memory", "constraint_closure", "persistence", "coherence"]
    )
    profile = meter.measure(sys)
    assert profile.ratio_endo_total is not None
    assert profile.memory_endo_ratio is not None
    assert profile.cba_theil_u is not None
    assert 0.0 <= profile.cba_theil_u <= 1.0
    assert profile.metadata["adapter"] == "PromisedCycle"


def test_unknown_metric_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown metric"):
        Autonometer(metrics=["not_a_real_metric"])
