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

    Every field is a *ratio of internal magnitude over total
    magnitude* and lives in ``[0.0, 1.0]``, so points in the profile
    are directly comparable across measurements. The two fields
    currently shipped span the canonical autonomy plane
    ``[0, 1] × [0, 1]``:

    - ``ratio_endo_total`` captures **closure**: how much of the
      next state is determined by the system's own previous state,
      once the environment is controlled for.
    - ``memory_endo_ratio`` captures **memory**: of the structural
      memory present in the joint (system, environment) trajectory,
      what fraction is carried by the system itself.

    Together, a point in ``(closure, memory)`` lets a caller tell
    apart drift, clockwork regularity, turbulence and candidate
    autopoietic organisation without tying the vocabulary to any
    single theory. The unifying argument behind the ratio shape is
    documented in ``docs/PBA.md``.

    Attributes
    ----------
    ratio_endo_total:
        Normalised conditional mutual information score of
        Albantakis / Bertschinger. In ``[0.0, 1.0]`` when computed.
        ``1.0`` means the system's next state is (given the
        environment) fully determined by its own previous state.
    memory_endo_ratio:
        Fraction of the joint structural memory carried by the
        system, computed as ``E(states) / (E(states) + E(env))``
        where ``E(.)`` is Crutchfield's excess entropy. In
        ``[0.0, 1.0]`` when computed. ``0.0`` means the trajectory's
        memory lives entirely in the environment (or, by convention,
        neither sequence carries memory at all); ``1.0`` means it
        lives entirely in the system. Replaces the absolute-bit
        ``structural_memory`` shipped in ``v0.3.x`` so that both
        primary axes share the ratio shape of the unifying argument.
    metadata:
        Free-form dictionary with contextual information about the
        measurement: which metrics were used, which adapter produced
        the inputs, sample sizes, seeds, timestamps, and similar.
    """

    ratio_endo_total: float | None = None
    memory_endo_ratio: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
