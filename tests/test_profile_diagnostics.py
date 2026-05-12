"""Tests for the optional diagnostic fields on :class:`AutonomyProfile`.

These tests exercise the ``return_diagnostics=True`` plumbing introduced
in ``v0.9.0a1``:

- the per-metric ``return_diagnostics`` path on ``compute_cba_theil_u``,
  ``compute_memory_endo_ratio`` and ``compute_rai_proxy_persistence``;
- the ``_METRIC_DIAGNOSTIC_FIELDS`` translation table in
  :mod:`autonometrics.core` that copies those diagnostics into the
  matching ``cba_*`` / ``memory_*`` / ``persistence_*`` fields on
  :class:`AutonomyProfile`;
- the public guarantee that diagnostic fields are ``None`` whenever the
  axis was not measured (mosaic dropout) and that adding them did not
  break the existing :class:`AutonomyProfile` construction signature.
"""

from __future__ import annotations

import warnings

import numpy as np
import pytest

import autonometrics as anm
from autonometrics import (
    Autonometer,
    AutonomyProfile,
    SimpleAutomaton,
    compute_cba_theil_u,
    compute_memory_endo_ratio,
    compute_rai_proxy_persistence,
)

# --------------------------------------------------------------------- #
# Minimal in-test adapters                                              #
# --------------------------------------------------------------------- #


class _DeclaredExecutedAdapter:
    """Adapter that exposes only the declared/executed protocol slot.

    The trajectory and environment are short on purpose so memory and
    persistence stay on mosaic dropout (their natural state for an
    adapter that does not implement ``replay_from_perturbation`` or a
    long enough trajectory).
    """

    def __init__(self, declared: np.ndarray, executed: np.ndarray) -> None:
        self._declared = np.asarray(declared, dtype=np.int64)
        self._executed = np.asarray(executed, dtype=np.int64)

    def get_state_history(self) -> np.ndarray:
        return self._executed.copy()

    def get_env_history(self) -> np.ndarray:
        return np.zeros_like(self._executed)

    def get_declared_executed(self) -> tuple[np.ndarray, np.ndarray]:
        return self._declared.copy(), self._executed.copy()


# --------------------------------------------------------------------- #
# Direct metric-level diagnostics                                       #
# --------------------------------------------------------------------- #


def test_coherence_metric_returns_diagnostics_dict() -> None:
    declared = np.tile(np.array([0, 1], dtype=np.int64), 128)
    executed = declared.copy()

    score, diagnostics = compute_cba_theil_u(declared, executed, return_diagnostics=True)

    assert score == pytest.approx(1.0)
    assert set(diagnostics) >= {"match_rate", "H_D", "H_E", "MI", "T"}
    assert diagnostics["match_rate"] == pytest.approx(1.0)
    assert diagnostics["H_D"] > 0.0
    assert diagnostics["MI"] == pytest.approx(diagnostics["H_D"])


def test_coherence_metric_bijection_loophole_diagnostic() -> None:
    """A label-bijection produces ``cba ≈ 1`` with ``match_rate = 0``."""
    declared = np.tile(np.array([0, 1], dtype=np.int64), 64)
    executed = 1 - declared

    score, diagnostics = compute_cba_theil_u(declared, executed, return_diagnostics=True)

    assert score == pytest.approx(1.0, abs=1e-6)
    assert diagnostics["match_rate"] == pytest.approx(0.0)


def test_memory_metric_returns_diagnostics_dict() -> None:
    rng = np.random.default_rng(0)
    states = rng.integers(0, 4, size=1024).astype(np.int64)
    env = rng.integers(0, 4, size=1024).astype(np.int64)

    score, diagnostics = compute_memory_endo_ratio(states, env, return_diagnostics=True)

    assert 0.0 <= score <= 1.0
    assert set(diagnostics) == {"e_states", "e_env"}
    assert diagnostics["e_states"] >= 0.0
    assert diagnostics["e_env"] >= 0.0


def test_persistence_metric_returns_diagnostics_dict() -> None:
    auto = SimpleAutomaton.demo(n_steps=512, seed=0)
    states = auto.get_state_history()
    env = auto.get_env_history()

    score, diagnostics = compute_rai_proxy_persistence(
        states,
        env,
        auto.replay_from_perturbation,
        n_perturbations=4,
        horizon=16,
        return_diagnostics=True,
    )

    assert 0.0 <= score <= 1.0
    assert set(diagnostics) == {"mean_hamming", "d_ref"}
    assert diagnostics["mean_hamming"] >= 0.0
    assert diagnostics["d_ref"] > 0.0


# --------------------------------------------------------------------- #
# Diagnostic propagation through ``Autonometer.measure``                #
# --------------------------------------------------------------------- #


def test_autonometer_populates_coherence_diagnostics_perfect_match() -> None:
    declared = np.tile(np.array([0, 1, 2, 3], dtype=np.int64), 64)
    executed = declared.copy()
    adapter = _DeclaredExecutedAdapter(declared, executed)

    profile = Autonometer(metrics=["coherence"]).measure(adapter)

    assert profile.cba_theil_u == pytest.approx(1.0)
    assert profile.cba_match_rate == pytest.approx(1.0)
    assert profile.cba_h_d is not None and profile.cba_h_d > 0.0
    assert profile.cba_h_e is not None and profile.cba_h_e > 0.0
    assert profile.cba_mi == pytest.approx(profile.cba_h_d)


def test_autonometer_populates_coherence_diagnostics_bijection_case() -> None:
    """The bijection regime is now visible from ``AutonomyProfile`` alone."""
    declared = np.tile(np.array([0, 1], dtype=np.int64), 128)
    executed = 1 - declared
    adapter = _DeclaredExecutedAdapter(declared, executed)

    profile = Autonometer(metrics=["coherence"]).measure(adapter)

    assert profile.cba_theil_u == pytest.approx(1.0, abs=1e-6)
    assert profile.cba_match_rate == pytest.approx(0.0)
    assert profile.cba_h_d is not None and profile.cba_h_d > 0.0


def test_autonometer_populates_memory_diagnostics_for_simple_automaton() -> None:
    auto = SimpleAutomaton.demo(n_steps=2000, seed=0)

    profile = Autonometer(metrics=["memory"]).measure(auto)

    assert profile.memory_endo_ratio is not None
    assert profile.memory_e_states is not None
    assert profile.memory_e_env is not None
    assert profile.memory_e_states >= 0.0
    assert profile.memory_e_env >= 0.0


def test_autonometer_populates_persistence_diagnostics_for_simple_automaton() -> None:
    auto = SimpleAutomaton.demo(n_steps=600, seed=0)

    profile = Autonometer(metrics=["persistence"]).measure(auto)

    assert profile.rai_proxy_persistence is not None
    assert profile.persistence_mean_hamming is not None
    assert profile.persistence_d_ref is not None
    assert profile.persistence_mean_hamming >= 0.0
    assert profile.persistence_d_ref > 0.0


# --------------------------------------------------------------------- #
# Mosaic-dropout / negative-space guarantees                            #
# --------------------------------------------------------------------- #


def test_diagnostics_for_unrequested_axis_remain_none() -> None:
    declared = np.tile(np.array([0, 1, 2], dtype=np.int64), 64)
    executed = declared.copy()
    adapter = _DeclaredExecutedAdapter(declared, executed)

    profile = Autonometer(metrics=["coherence"]).measure(adapter)

    # Coherence axis is populated.
    assert profile.cba_theil_u is not None
    assert profile.cba_match_rate is not None
    # Other axes were never asked for: their diagnostics must stay None.
    assert profile.memory_endo_ratio is None
    assert profile.memory_e_states is None
    assert profile.memory_e_env is None
    assert profile.rai_proxy_persistence is None
    assert profile.persistence_mean_hamming is None
    assert profile.persistence_d_ref is None


def test_coherence_diagnostics_none_when_adapter_lacks_protocol() -> None:
    """An adapter without ``get_declared_executed`` reports no CBA."""
    auto = SimpleAutomaton.demo(n_steps=600, seed=0)

    profile = Autonometer(metrics=["coherence"]).measure(auto)

    assert profile.cba_theil_u is None
    assert profile.cba_match_rate is None
    assert profile.cba_h_d is None
    assert profile.cba_h_e is None
    assert profile.cba_mi is None


# --------------------------------------------------------------------- #
# AutonomyProfile construction surface                                  #
# --------------------------------------------------------------------- #


def test_autonomy_profile_constructs_without_diagnostic_arguments() -> None:
    """The new fields default to ``None`` and the existing signature still works."""
    profile = AutonomyProfile(
        ratio_endo_total=0.5,
        memory_endo_ratio=0.3,
    )

    assert profile.ratio_endo_total == 0.5
    assert profile.memory_endo_ratio == 0.3
    assert profile.cba_match_rate is None
    assert profile.cba_h_d is None
    assert profile.cba_h_e is None
    assert profile.cba_mi is None
    assert profile.memory_e_states is None
    assert profile.memory_e_env is None
    assert profile.persistence_mean_hamming is None
    assert profile.persistence_d_ref is None


def test_top_level_measure_propagates_diagnostics() -> None:
    declared = np.tile(np.array([0, 1, 2, 3], dtype=np.int64), 64)
    executed = declared.copy()
    adapter = _DeclaredExecutedAdapter(declared, executed)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        profile = anm.measure(adapter, axes=["coherence"])

    assert profile.cba_theil_u == pytest.approx(1.0)
    assert profile.cba_match_rate == pytest.approx(1.0)
