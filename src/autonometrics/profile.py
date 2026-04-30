"""Data container for the output of an autonomy measurement."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AutonomyProfile:
    """A structural self-determination profile of a system.

    The profile is a small vector of named, substrate-independent
    measurements. Every field is ``Optional[float]``: a given metric
    only populates the field it is responsible for, and fields not
    measured on this run stay ``None``. This keeps the profile
    honest — a caller can tell at a glance what was and was not
    computed — and makes the dataclass extensible without breaking
    older consumers.

    Attributes
    ----------
    ratio_endo_total:
        Normalised conditional mutual information score of
        Albantakis / Bertschinger. In ``[0.0, 1.0]`` when computed.
        ``1.0`` means the system's next state is (given the
        environment) fully determined by its own previous state.
    autopoietic_ratio:
        Fernandez-Gershenson autopoietic ratio,
        ``C(system) / C(environment)`` with
        ``C(x) = 4 * E(x) * (1 - E(x))`` on the normalised Shannon
        entropy ``E``. Natural range is ``[0.0, +inf)``: values above
        ``1.0`` mean the system is more complex than its environment.
    metadata:
        Free-form dictionary with contextual information about the
        measurement: which metrics were used, which adapter produced
        the inputs, sample sizes, seeds, timestamps, and similar.
    """

    ratio_endo_total: float | None = None
    autopoietic_ratio: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
