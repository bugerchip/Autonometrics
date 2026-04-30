"""Tests for the AutonomyProfile data container."""

import dataclasses

import pytest

from autonometrics import AutonomyProfile


def test_profile_has_expected_fields() -> None:
    profile = AutonomyProfile(ratio_endo_total=0.5)
    assert profile.ratio_endo_total == 0.5
    assert profile.metadata == {}


def test_profile_accepts_metadata() -> None:
    profile = AutonomyProfile(
        ratio_endo_total=0.42,
        metadata={"metric": "albantakis", "n_steps": 1000},
    )
    assert profile.metadata["metric"] == "albantakis"
    assert profile.metadata["n_steps"] == 1000


def test_profile_is_frozen() -> None:
    profile = AutonomyProfile(ratio_endo_total=0.1)
    with pytest.raises(dataclasses.FrozenInstanceError):
        profile.ratio_endo_total = 0.9  # type: ignore[misc]


def test_profile_field_types() -> None:
    fields = {f.name: f.type for f in dataclasses.fields(AutonomyProfile)}
    assert fields["ratio_endo_total"] == "float"
    assert fields["metadata"] == "dict[str, Any]"


def test_profile_default_metadata_is_independent() -> None:
    a = AutonomyProfile(ratio_endo_total=0.0)
    b = AutonomyProfile(ratio_endo_total=1.0)
    a.metadata["shared"] = "value"
    assert "shared" not in b.metadata
