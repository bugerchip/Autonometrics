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
    constraint_closure:
        Montévil & Mossio-style constraint-closure ratio. In
        ``[0.0, 1.0]`` when computed. The fraction of the
        system's update functions (constraints) that lie on at
        least one simple directed cycle of length 2 or 3 in the
        causal dependency graph. ``0.0`` means no constraints
        sustain each other through short feedback loops (e.g. a
        single-node system, or a pure feed-forward dependency
        chain); ``1.0`` means every constraint is part of such a
        loop. Operationalises a topological proxy for the
        biological notion of organisational closure; details and
        falsification criteria live in
        ``docs/CONSTRAINT_CLOSURE.md``.
    rai_proxy_persistence:
        Lee & McShea-style perturbation-persistence proxy. In
        ``[0.0, 1.0]`` when computed. Measures how strongly the
        system returns to its own unperturbed trajectory after a
        single-element perturbation, normalised against the chance
        baseline of two independent random trajectories of the
        same focal alphabet. ``1.0`` means perturbations are
        absorbed perfectly; ``0.0`` means perturbations propagate
        as much as random noise. Operationalises a structural
        autonomous-motivation proxy from Self-Determination Theory
        (Deci & Ryan); the design rationale and validation plan
        live in ``docs/RAI.md``. The metric is a *structural
        proxy* for the autonomous-vs-controlled motivation
        distinction; strong validation against transcript-based
        RAI scoring is deferred to ``v0.9.0``.
    metadata:
        Free-form dictionary with contextual information about the
        measurement: which metrics were used, which adapter produced
        the inputs, sample sizes, seeds, timestamps, and similar.
    """

    ratio_endo_total: float | None = None
    memory_endo_ratio: float | None = None
    constraint_closure: float | None = None
    rai_proxy_persistence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
