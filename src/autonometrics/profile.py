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

    The two current fields map to the two axes of the *autonomy plane*:

    - ``ratio_endo_total`` captures **closure**: how much of the next
      state is determined by the system's own previous state, once the
      environment is controlled for.
    - ``structural_memory`` captures **memory**: how many bits of the
      trajectory's past are useful for predicting its future.

    Together, a point in ``(closure, memory)`` space lets us tell
    apart drift, clockwork regularity, turbulence and candidate
    autopoietic organisation without tying the vocabulary to any
    single theory.

    Attributes
    ----------
    ratio_endo_total:
        Normalised conditional mutual information score of
        Albantakis / Bertschinger. In ``[0.0, 1.0]`` when computed.
        ``1.0`` means the system's next state is (given the
        environment) fully determined by its own previous state.
    structural_memory:
        Crutchfield excess entropy of the state trajectory, in bits.
        Zero for constant or i.i.d. noise sequences; ``log2(p)`` for a
        deterministic period-``p`` cycle; positive in general for
        sequences with non-trivial temporal structure. Replaces the
        LMC-based autopoietic ratio used in ``v0.2.x``, which
        collapsed to zero on ordered systems.
    metadata:
        Free-form dictionary with contextual information about the
        measurement: which metrics were used, which adapter produced
        the inputs, sample sizes, seeds, timestamps, and similar.
    """

    ratio_endo_total: float | None = None
    structural_memory: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
