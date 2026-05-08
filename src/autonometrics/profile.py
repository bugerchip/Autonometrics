"""Data container for the output of an autonomy measurement."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Canonical public axis names used by the user-facing API. Mirrors
# ``autonometrics.core.AXES`` (declared here too to avoid an import
# cycle between ``core`` and ``profile``).
_CANONICAL_AXES: tuple[str, ...] = (
    "closure",
    "memory",
    "constraint",
    "persistence",
    "coherence",
)

# Translation: canonical public name -> internal field on AutonomyProfile.
_CANONICAL_TO_FIELD: dict[str, str] = {
    "closure": "ratio_endo_total",
    "memory": "memory_endo_ratio",
    "constraint": "constraint_closure",
    "persistence": "rai_proxy_persistence",
    "coherence": "cba_theil_u",
}


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
    cba_theil_u:
        Information-theoretic CBA proxy (Theil-U style). In
        ``[0.0, 1.0]`` when computed; ``None`` when the adapter
        does not expose a declarative layer. Computed as
        ``I(D; E) / H(D)`` with Miller-Madow bias correction,
        where ``D`` is the system's *declared* trajectory and
        ``E`` is its *executed* trajectory. ``1.0`` means knowing
        the executed trajectory removes all uncertainty about the
        declared one (the declaration is fully informative about
        the execution); ``0.0`` means execution is statistically
        independent of declaration. Operationalises the
        intention–execution gap (Aristotle's *akrasia*; Festinger
        1957; Sheeran 2002; Lanham 2023; PhilArchive 2024) as a
        structural ratio. The design rationale, candidate
        alternatives and validation plan live in ``docs/CBA.md``;
        validation against external behavioural data
        (FAITHCOT-BENCH, Sheeran-style intention–behaviour
        regressions) is deferred to ``v0.9.0``.

    Optional diagnostic fields
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    The following ``Optional[float]`` fields surface intermediate
    magnitudes that the underlying metrics already compute
    internally. They are populated by ``Autonometer.measure`` (and
    the top-level ``measure`` convenience function) for axes whose
    metric supports a ``return_diagnostics=True`` path; ``None``
    otherwise (axis not requested, adapter does not support the
    axis, or metric does not yet expose diagnostics). All values
    are dimensionless and consistent with the ratio definitions
    documented for each axis. Added in ``v0.9.0a1``;
    backwards-compatible (default ``None``).

    cba_match_rate:
        Fraction of timesteps with pointwise equality between the
        declared and executed trajectories, ``mean(D_t == E_t)``.
        Companion to ``cba_theil_u``. Useful when the score has
        already been normalised and a downstream consumer also
        wants the raw match magnitude.
    cba_h_d:
        Miller-Madow-corrected Shannon entropy of the declared
        marginal in bits. Denominator of ``cba_theil_u``.
    cba_h_e:
        Miller-Madow-corrected Shannon entropy of the executed
        marginal in bits.
    cba_mi:
        Mutual information ``I(D; E)`` in bits, computed as
        ``H(D) + H(E) - H(D, E)`` with Miller-Madow correction
        applied to each entropy. Numerator of ``cba_theil_u``.
    memory_e_states:
        Crutchfield excess entropy of the system trajectory in
        bits. Numerator of ``memory_endo_ratio``. ``0.0`` when the
        sequence is too short for the block-length cap or has no
        block-level structure.
    memory_e_env:
        Crutchfield excess entropy of the environment trajectory
        in bits. Component of the denominator of
        ``memory_endo_ratio``.
    persistence_mean_hamming:
        Mean post-perturbation Hamming mismatch between perturbed
        and unperturbed focal trajectories, averaged over
        ``n_perturbations`` independent perturbation times.
        Empirical numerator of the persistence score.
    persistence_d_ref:
        Empirical chance-baseline Hamming distance,
        ``1 - sum(p_a ** 2)``, computed from the focal marginal
        distribution. Denominator used to normalise the persistence
        score against a same-alphabet random baseline.

    metadata:
        Free-form dictionary with contextual information about the
        measurement: which metrics were used, which adapter produced
        the inputs, sample sizes, seeds, timestamps, and similar.
    """

    ratio_endo_total: float | None = None
    memory_endo_ratio: float | None = None
    constraint_closure: float | None = None
    rai_proxy_persistence: float | None = None
    cba_theil_u: float | None = None

    # Optional diagnostic quantities (since v0.9.0a1). All default to
    # ``None`` so that existing consumers see no behavioural change.
    cba_match_rate: float | None = None
    cba_h_d: float | None = None
    cba_h_e: float | None = None
    cba_mi: float | None = None
    memory_e_states: float | None = None
    memory_e_env: float | None = None
    persistence_mean_hamming: float | None = None
    persistence_d_ref: float | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Canonical public API (since v0.8.1a0).
    # The five named properties below mirror the canonical axes exposed
    # in ``autonometrics.AXES`` and the README. Internal field names
    # (``ratio_endo_total`` etc.) are kept untouched for backward
    # compatibility but are no longer the recommended access path.
    # ------------------------------------------------------------------

    @property
    def closure(self) -> float | None:
        """Canonical alias for :attr:`ratio_endo_total` (Albantakis closure)."""
        return self.ratio_endo_total

    @property
    def memory(self) -> float | None:
        """Canonical alias for :attr:`memory_endo_ratio`."""
        return self.memory_endo_ratio

    @property
    def constraint(self) -> float | None:
        """Canonical alias for :attr:`constraint_closure` (Mossio)."""
        return self.constraint_closure

    @property
    def persistence(self) -> float | None:
        """Canonical alias for :attr:`rai_proxy_persistence`."""
        return self.rai_proxy_persistence

    @property
    def coherence(self) -> float | None:
        """Canonical alias for :attr:`cba_theil_u` (CBA / Theil's U)."""
        return self.cba_theil_u

    def __getitem__(self, name: str) -> float | None:
        """Look up an axis value by canonical or internal name.

        Examples
        --------
        >>> profile["closure"]   # canonical
        >>> profile["albantakis"]  # internal (still works)
        """
        if name in _CANONICAL_TO_FIELD:
            return getattr(self, _CANONICAL_TO_FIELD[name])
        if hasattr(self, name) and name in {
            "ratio_endo_total",
            "memory_endo_ratio",
            "constraint_closure",
            "rai_proxy_persistence",
            "cba_theil_u",
        }:
            return getattr(self, name)
        # Tolerate the internal metric identifier "albantakis" too.
        if name == "albantakis":
            return self.ratio_endo_total
        raise KeyError(
            f"Unknown axis {name!r}. "
            f"Canonical axes: {_CANONICAL_AXES}."
        )

    def to_dict(self) -> dict[str, float | None]:
        """Return a flat ``{canonical_axis: value_or_None}`` dictionary.

        The output uses canonical public names only (``closure``,
        ``memory``, ``constraint``, ``persistence``, ``coherence``),
        making the result trivially JSON-serialisable and stable
        against future renames of internal fields.
        """
        return {axis: getattr(self, _CANONICAL_TO_FIELD[axis]) for axis in _CANONICAL_AXES}

    def defined_axes(self) -> list[str]:
        """List the canonical axes that were actually computed.

        An axis is considered *defined* iff its value is not ``None``.
        Mirrors the mosaic-dropout policy: adapters that do not support
        a given axis report ``None`` for that field, and this method
        filters those out.
        """
        return [axis for axis, value in self.to_dict().items() if value is not None]

    def __repr__(self) -> str:
        """Multi-line, human-readable summary using canonical names.

        Only axes with a non-``None`` value are listed in the body.
        Adapter and key metadata are summarised in a compact header.
        """
        adapter = self.metadata.get("adapter", "?")
        n_steps = self.metadata.get("n_timesteps")
        defined = self.to_dict()
        defined_lines = [
            f"  {axis:<12s} = {value:.4f}"
            for axis, value in defined.items()
            if value is not None
        ]
        missing = [axis for axis, value in defined.items() if value is None]

        header = f"AutonomyProfile(adapter={adapter!r}"
        if n_steps is not None:
            header += f", n_timesteps={n_steps}"
        header += ")"

        body = "\n".join(defined_lines) if defined_lines else "  (no axes computed)"
        footer = f"  missing: {missing}" if missing else ""

        parts = [header, body]
        if footer:
            parts.append(footer)
        return "\n".join(parts)
