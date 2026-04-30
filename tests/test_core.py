"""Tests for the Autonometer orchestrator."""

import pytest

from autonometrics import Autonometer


def test_default_metric_is_albantakis() -> None:
    meter = Autonometer()
    assert meter.metric == "albantakis"


def test_unknown_metric_raises() -> None:
    with pytest.raises(ValueError, match="Unknown metric"):
        Autonometer(metric="does-not-exist")


def test_measure_raises_not_implemented_in_v010a0() -> None:
    meter = Autonometer()
    with pytest.raises(NotImplementedError):
        meter.measure(object())
