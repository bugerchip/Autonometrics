"""Data container for the output of an autonomy measurement."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AutonomyProfile:
    """A structural self-determination profile of a system.

    Currently a single-dimension profile. The shape is intentionally
    kept simple in v0.1: additional dimensions (drift, phase stability,
    boundary hardness, temporal integral) will be added as more metrics
    are implemented.

    Attributes
    ----------
    ratio_endo_total:
        Proportion of the system's next-state determination that comes
        from its own previous state versus the environment. Expected
        to lie in ``[0.0, 1.0]``, where ``1.0`` means the system's
        dynamics are fully self-determined (given the environment) and
        ``0.0`` means the next state is entirely driven by the
        environment. Range is not enforced at construction time; it is
        the responsibility of the metric implementation to return a
        valid value.
    metadata:
        Free-form dictionary with contextual information about the
        measurement: which metric was used, which adapter produced the
        inputs, sample sizes, seeds, timestamps, etc.
    """

    ratio_endo_total: float
    metadata: dict[str, Any] = field(default_factory=dict)
