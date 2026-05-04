"""Tests for the canonical public API introduced in v0.8.1a0.

The pre-existing internal vocabulary (``albantakis``, ``ratio_endo_total``,
``cba_theil_u``, ...) is preserved for backward compatibility. This
module validates that the canonical public names (``closure``,
``memory``, ``constraint``, ``persistence``, ``coherence``) work
everywhere the old names worked, and that the new convenience helpers
(``measure`` top-level, ``AutonomyProfile.to_dict``, etc.) behave as
documented.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

import autonometrics as anm
from autonometrics import AXES, ALL_AXES, AutonomyProfile, PromisedCycle


# --------------------------------------------------------------------- #
# Module-level constants
# --------------------------------------------------------------------- #


def test_axes_constant_exposes_five_canonical_names() -> None:
    assert AXES == ("closure", "memory", "constraint", "persistence", "coherence")


def test_all_axes_alias_matches_axes() -> None:
    assert ALL_AXES is AXES or ALL_AXES == AXES


def test_axes_constant_is_tuple_not_list() -> None:
    """Canonical axes are immutable — callers must not mutate them."""
    assert isinstance(AXES, tuple)


# --------------------------------------------------------------------- #
# Autonometer accepts canonical names
# --------------------------------------------------------------------- #


def _ref_system() -> PromisedCycle:
    return PromisedCycle(length=600, period=4, alphabet=4, p_noise=0.05, seed=42)


def test_autonometer_accepts_canonical_metric_names() -> None:
    meter = anm.Autonometer(metrics=["closure", "memory", "coherence"])
    profile = meter.measure(_ref_system())
    assert profile.closure is not None
    assert profile.memory is not None
    assert profile.coherence is not None


def test_autonometer_default_runs_all_five_axes() -> None:
    """Default behaviour: ``Autonometer()`` measures all five axes.

    ``PromisedCycle`` exposes a state trajectory, a replay function and
    a declarative layer, so it qualifies for ``closure``, ``memory``,
    ``persistence`` and ``coherence``. It does not expose a causal
    graph, so ``constraint`` is mosaic-dropped to ``None`` (consistent
    with the v0.8.0a0 atlas-as-mosaic verdict).
    """
    meter = anm.Autonometer()
    profile = meter.measure(_ref_system())
    assert profile.closure is not None
    assert profile.memory is not None
    assert profile.persistence is not None
    assert profile.coherence is not None
    assert profile.constraint is None


def test_autonometer_internal_names_still_work() -> None:
    """Backward compatibility: old internal identifiers remain valid."""
    meter = anm.Autonometer(metrics=["albantakis", "constraint_closure"])
    profile = meter.measure(_ref_system())
    assert profile.closure is not None
    assert profile.constraint is None  # adapter doesn't expose graph


def test_autonometer_canonical_and_internal_can_mix() -> None:
    meter = anm.Autonometer(metrics=["closure", "albantakis", "memory"])
    profile = meter.measure(_ref_system())
    assert profile.closure is not None


def test_autonometer_unknown_name_raises_clear_error() -> None:
    with pytest.raises(ValueError, match="Unknown metric"):
        anm.Autonometer(metrics=["totally_made_up"])


# --------------------------------------------------------------------- #
# AutonomyProfile canonical accessors
# --------------------------------------------------------------------- #


def test_profile_canonical_properties_match_internal_fields() -> None:
    profile = AutonomyProfile(
        ratio_endo_total=0.8,
        memory_endo_ratio=0.6,
        constraint_closure=0.4,
        rai_proxy_persistence=0.2,
        cba_theil_u=0.1,
    )
    assert profile.closure == 0.8
    assert profile.memory == 0.6
    assert profile.constraint == 0.4
    assert profile.persistence == 0.2
    assert profile.coherence == 0.1


def test_profile_getitem_canonical_names() -> None:
    profile = AutonomyProfile(ratio_endo_total=0.5)
    assert profile["closure"] == 0.5


def test_profile_getitem_internal_names_still_supported() -> None:
    profile = AutonomyProfile(ratio_endo_total=0.5)
    assert profile["albantakis"] == 0.5
    assert profile["ratio_endo_total"] == 0.5


def test_profile_getitem_unknown_raises_keyerror() -> None:
    profile = AutonomyProfile()
    with pytest.raises(KeyError, match="Unknown axis"):
        _ = profile["nonexistent"]


def test_profile_to_dict_uses_canonical_names() -> None:
    profile = AutonomyProfile(
        ratio_endo_total=0.8,
        memory_endo_ratio=0.6,
        constraint_closure=None,
        rai_proxy_persistence=0.2,
        cba_theil_u=None,
    )
    d = profile.to_dict()
    assert set(d.keys()) == set(AXES)
    assert d["closure"] == 0.8
    assert d["memory"] == 0.6
    assert d["constraint"] is None
    assert d["persistence"] == 0.2
    assert d["coherence"] is None


def test_profile_to_dict_is_json_serialisable() -> None:
    profile = AutonomyProfile(ratio_endo_total=0.5, cba_theil_u=None)
    blob = json.dumps(profile.to_dict())
    assert "closure" in blob
    assert "coherence" in blob


def test_profile_defined_axes_filters_none() -> None:
    profile = AutonomyProfile(
        ratio_endo_total=0.8,
        memory_endo_ratio=0.6,
        constraint_closure=None,
        rai_proxy_persistence=None,
        cba_theil_u=0.1,
    )
    assert profile.defined_axes() == ["closure", "memory", "coherence"]


def test_profile_defined_axes_empty_when_all_none() -> None:
    profile = AutonomyProfile()
    assert profile.defined_axes() == []


def test_profile_repr_lists_only_defined_axes() -> None:
    profile = AutonomyProfile(
        ratio_endo_total=0.8,
        memory_endo_ratio=None,
        constraint_closure=None,
        rai_proxy_persistence=None,
        cba_theil_u=None,
        metadata={"adapter": "PromisedCycle", "n_timesteps": 600},
    )
    text = repr(profile)
    assert "closure" in text
    assert "PromisedCycle" in text
    assert "0.8000" in text  # closure value
    # "missing" line should mention the four absent axes
    assert "memory" in text


# --------------------------------------------------------------------- #
# Top-level ``measure()`` convenience function
# --------------------------------------------------------------------- #


def test_measure_top_level_runs_all_five_by_default() -> None:
    profile = anm.measure(_ref_system())
    assert isinstance(profile, AutonomyProfile)
    assert profile.closure is not None
    assert profile.memory is not None
    assert profile.coherence is not None


def test_measure_top_level_accepts_axes_subset() -> None:
    profile = anm.measure(_ref_system(), axes=["closure"])
    assert profile.closure is not None
    assert profile.memory is None
    assert profile.coherence is None


def test_measure_top_level_accepts_canonical_or_internal_mix() -> None:
    profile = anm.measure(_ref_system(), axes=["closure", "albantakis"])
    assert profile.closure is not None


def test_measure_top_level_metadata_lists_canonical_axes() -> None:
    profile = anm.measure(_ref_system(), axes=["closure", "memory"])
    assert "axes" in profile.metadata
    assert set(profile.metadata["axes"]) == {"closure", "memory"}


# --------------------------------------------------------------------- #
# Compute aliases at top level
# --------------------------------------------------------------------- #


def test_compute_aliases_are_same_callable_as_originals() -> None:
    assert anm.compute_closure is anm.compute_albantakis
    assert anm.compute_constraint is anm.compute_constraint_closure
    assert anm.compute_persistence is anm.compute_rai_proxy_persistence
    assert anm.compute_coherence is anm.compute_cba_theil_u
    assert anm.compute_memory is anm.compute_memory_endo_ratio


def test_compute_closure_alias_runs_end_to_end() -> None:
    states = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1], dtype=np.int64)
    env = np.zeros_like(states)
    score = anm.compute_closure(states, env)
    assert 0.0 <= score <= 1.0
