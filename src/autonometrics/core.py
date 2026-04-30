"""Core orchestrator for autonomy measurements."""

from __future__ import annotations

from typing import Any

from autonometrics.profile import AutonomyProfile

SUPPORTED_METRICS: frozenset[str] = frozenset({"albantakis"})


class Autonometer:
    """Orchestrator that applies a metric to a system and returns a profile.

    Parameters
    ----------
    metric:
        Identifier of the metric to use. Currently only ``"albantakis"``
        is accepted. Additional metrics (Gershenson autopoietic ratio,
        SDT Relative Autonomy Index, Coherence-Based Alignment) will be
        registered here.
    """

    def __init__(self, metric: str = "albantakis") -> None:
        if metric not in SUPPORTED_METRICS:
            raise ValueError(f"Unknown metric {metric!r}. Supported: {sorted(SUPPORTED_METRICS)}")
        self.metric = metric

    def measure(self, system: Any) -> AutonomyProfile:
        """Compute the autonomy profile of ``system``.

        In v0.1.0a0 the measurement logic is not yet implemented;
        calling this method raises ``NotImplementedError``. The metric
        implementation lands in the next commit.
        """
        raise NotImplementedError(
            "Autonometer.measure is not implemented yet. "
            "The Albantakis metric will be wired in the next commit."
        )
