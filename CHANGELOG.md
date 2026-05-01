# Changelog

All notable changes to `autonometrics` are documented in this file.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [PEP 440](https://peps.python.org/pep-0440/)
version numbering. Until the first non-alpha release every minor
version may introduce breaking changes.

## [0.4.0a0] - 2026-04-30

### Changed (breaking)

- **Replaced absolute-bit `compute_excess_entropy` with the
  ratio-shaped `compute_memory_endo_ratio`.** The previous metric
  returned a magnitude in bits, which broke the package's unifying
  argument that every integrated formalisation of structural
  self-determination shares the form `internal / total`. The new
  metric reuses Crutchfield's excess-entropy estimator internally
  (now a private helper) and applies it to both the system and the
  environment, returning the fraction of the joint structural memory
  carried by the system: `E(states) / (E(states) + E(env))`. The
  result is dimensionless and lives in `[0.0, 1.0]`, directly
  comparable with the closure axis from `compute_albantakis`.
- `AutonomyProfile.structural_memory` renamed to
  `AutonomyProfile.memory_endo_ratio`.
- The metric identifier `"memory"` now maps to
  `compute_memory_endo_ratio` and writes to `memory_endo_ratio` in
  the profile.

### Added

- `src/autonometrics/metrics/memory_ratio.py` — the new metric, with
  the excess-entropy estimator and Grassberger-style block-length
  cap kept as private helpers.
- `tests/test_memory_ratio.py` — canonical cases covering constant
  pairs, structured-vs-iid asymmetry, balanced structure, and the
  validation paths.
- README rewritten around the **Principio de Bordes Autodeterminados
  (PBA)** convention: every metric in the package shares the
  `internal / total` ratio shape, and the autonomy plane is now
  explicitly framed as the canonical `[0, 1] x [0, 1]` space.
  Roadmap reorganised around adding more ratios in the same shape
  rather than around adding features.

### Removed

- `src/autonometrics/metrics/excess_entropy.py` — the public
  absolute-bit entry point; the underlying estimator survives as a
  private helper inside `memory_ratio.py`.
- `tests/test_excess_entropy.py`.

### Rationale

The package's unifying convention is that every shipped metric
follows the same `internal / total` ratio shape, so points from
different metrics live in the same comparable space. The
absolute-bit excess entropy used in `v0.3.x` broke that convention
by introducing an inhomogeneous axis on the autonomy plane.
`v0.4.0a0` restores the convention so all primary metrics are
ratios in `[0, 1]` and the autonomy plane is canonical
`[0, 1] x [0, 1]`. The full statement of the convention as a
falsifiable working hypothesis lives in `docs/PBA.md`.

## [0.3.0a0] - 2026-04-30

### Changed (breaking)

- **Replaced the LMC-based `autopoietic_ratio` with Crutchfield excess
  entropy.** The previous metric, `C = 4 * E * (1 - E)` on the
  normalised Shannon entropy, collapses to zero on both highly
  ordered and highly disordered sequences, which Feldman & Crutchfield
  (2002) showed is a structural weakness of LMC-style "balance"
  measures. The new `compute_excess_entropy` estimates the number of
  bits of past useful for predicting the future via block-entropy
  saturation, with a Grassberger-style rule for the effective block
  length so i.i.d. noise does not pick up phantom structure from
  undersampling.
- `AutonomyProfile.autopoietic_ratio` has been renamed to
  `AutonomyProfile.structural_memory` and its semantics are now bits
  of memory rather than a complexity ratio.
- The metric identifier `"autopoietic"` has been renamed to
  `"memory"`. `Autonometer(metrics=["autopoietic"])` now raises
  `ValueError`.
- `compute_autopoietic_ratio` has been removed and replaced by
  `compute_excess_entropy`.

### Added

- `src/autonometrics/metrics/excess_entropy.py` — the new metric
  implementation, with an auto-capped effective block length.
- `tests/test_excess_entropy.py` — canonical cases covering constant
  series, i.i.d. noise, period-4 and period-8 cycles, ordered vs
  noise comparison, length mismatch, short-series rejection, invalid
  block length, and env-argument independence.
- `README.md`: "The autonomy plane" section (four quadrants:
  drift / clockwork / turbulence / candidate autopoietic corner) and
  a "Theoretical grounding" section pointing to Farnsworth (2018),
  Crutchfield & Young (1989), Feldman & Crutchfield (2002), and
  Langton (1990).
- `examples/automaton_demo.py` now compares **three** systems
  (self-ruled, environment-driven, mixed 70/30) and prints where each
  lands on the plane.

### Removed

- `src/autonometrics/metrics/gershenson.py`.
- `tests/test_gershenson.py`.
- Every reference to LMC, `autopoietic_ratio` and the Gershenson
  metric in docstrings, READMEs, and demos.

### Rationale

The point of moving away from LMC is not to discard autopoiesis as a
biological concept; it is to stop using a mathematical instrument
(balance of order and disorder) that is provably blind to the
structured cycles we most want the package to detect. Excess entropy
gives ``log2(p)`` for a period-``p`` cycle, ``0`` for i.i.d. noise,
and positive values for sequences with genuine long-range structure,
which is the behaviour the "memory" axis of the autonomy plane
requires.

## [0.2.0a0] - 2026-04-29

### Added

- Fernandez-Gershenson autopoietic ratio (`compute_autopoietic_ratio`)
  as a second metric. *(Removed in 0.3.0a0.)*
- `AutonomyProfile.autopoietic_ratio` optional field. *(Renamed in
  0.3.0a0.)*
- `Autonometer` multi-metric support via the `metrics=[...]`
  parameter; `metric=` kept for backward compatibility.
- `CSVTrajectory` adapter (`from_path`, `from_arrays`) for
  externally-supplied discrete trajectories.
- `examples/csv_demo.py`.

## [0.1.0a0] - 2026-04-29

### Added

- Initial release with Albantakis-style conditional mutual information
  metric (`compute_albantakis`, returning `ratio_endo_total`).
- `SimpleAutomaton` adapter with self-generated and
  externally-imposed rule constructors.
- `Autonometer` orchestrator and `AutonomyProfile` data container.
- CI pipeline, `pytest` and `ruff` configuration.
