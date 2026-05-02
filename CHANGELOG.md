# Changelog

All notable changes to `autonometrics` are documented in this file.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [PEP 440](https://peps.python.org/pep-0440/)
version numbering. Until the first non-alpha release every minor
version may introduce breaking changes.

## [0.5.1a0] - 2026-05-01

### Added

- `examples/saturation_diagnostic.py` — controlled experiment that
  injects Bernoulli bit-flip noise into the focal trajectory of a
  saturating elementary cellular automaton (rule 110 by default),
  sweeps the noise probability `p ∈ {0, 0.01, 0.02, 0.05, 0.10,
  0.15, 0.20, 0.30, 0.40, 0.50}`, runs five independent seeds per
  level, and reports closure / memory mean ± std per level. Adds a
  diagnosis line that flags whether the curve drops monotonically
  off the saturation wall as the closure-saturation theorem
  predicts.
- `examples/saturation_plot.py` — optional matplotlib renderer
  that loads the diagnostic CSV and writes a closure-vs-noise
  curve PNG with error bars. Available via the existing `viz`
  extra (`pip install autonometrics[viz]`).
- `tests/benchmarks/test_saturation_smoke.py` — 8 smoke tests
  covering the noise wrapper (zero-noise reproduces the base ECA
  exactly, non-zero noise diverges in the focal trajectory but
  preserves the environment, parameter validation), and the sweep
  helpers (quick-mode shape, zero-noise saturation recovery, high-
  noise drop, CSV well-formedness, aggregation grouping).
- `tests/benchmarks/test_saturation_plot_smoke.py` — 4 smoke
  tests skipped when matplotlib is absent, covering CSV coercion,
  per-noise aggregation, PNG rendering, and the empty-CSV failure
  path.
- `docs/benchmarks/saturation_v0.5.1.csv` — snapshot of the full
  diagnostic run (10 noise levels × 5 seeds = 50 valid points).
- `docs/benchmarks/saturation_v0.5.1.png` — closure-vs-noise curve
  rendered from the CSV above. Closure drops from 1.000 ± 0.000 at
  `p = 0` to 0.001 ± 0.001 at `p = 0.5`, monotonically. Memory
  declines more gradually and plateaus around 0.07.
- `docs/benchmarks/saturation_v0.5.1.log.txt` — captured stdout
  of the reference run, including the diagnosis line.
- New section "Domain of applicability" in `docs/PBA.md` and
  `docs/PBA.es.md`. Formalises the closure-saturation theorem
  (`A = 1` by construction for any deterministic system whose
  observed `(S, E)` covers the transition rule's inputs), records
  the empirical confirmation from the diagnostic, and spells out
  three consequences for the PBA hypothesis: trivial regions are
  expected, the system / environment cut shifts the metric, and
  PBA's predictions are conditional on benchmark systems staying
  outside those regions.

### Findings

- The closure-saturation observed in the `v0.5.0a0` benchmark is a
  theorem about the metric on deterministic, fully-observed
  systems — not a flaw of the metric and not specific to ECA.
  Three of the four adapter classes (ECA, PeriodicCycle,
  SimpleAutomaton.self_generated) satisfy the theorem's
  preconditions; KauffmanNetwork breaks them because the focal
  node's `K` neighbours can lie outside the observed `(S, E)`
  pair, which is exactly why Kauffman closures vary continuously
  in the benchmark snapshot.
- The saturation wall is **fragile**, not robust. Adding `p = 0.01`
  bit-flip noise (one flipped bit per hundred timesteps) drops
  closure from `1.000` to `0.81 ± 0.05`. The wall is therefore an
  isolated theoretical point, and any closure value below 1.0 in
  practice is informative about partial observation, stochastic
  dynamics or measurement noise.

## [0.5.0a0] - 2026-05-01

### Added

- `src/autonometrics/benchmarks/` subpackage with three reference
  systems: `ECASystem` (elementary cellular automaton),
  `KauffmanNetwork` (synchronous random Boolean network with tunable
  focal coupling), and `PeriodicCycle` (deterministic period-`p`
  control). All three implement the existing `AutonomySystem`
  protocol and ship inside the installable package, so
  `pip install autonometrics` is enough to reproduce any benchmark
  figure shipped with this release.
- `tests/benchmarks/` with 37 unit tests covering shape, dtype,
  alphabet, reproducibility, and smoke integration with
  `Autonometer`.
- `examples/benchmark_demo.py` — orchestrator that sweeps the three
  benchmark systems plus `SimpleAutomaton` over multiple seeds,
  measures `closure` and `memory` for each, prints the per-row table,
  and writes a snapshot CSV. Reports Pearson and Spearman
  correlation between the two axes and emits a `Diagnosis` line keyed
  to the `|r| < 0.7` falsification threshold from `docs/PBA.md`.
- `examples/benchmark_plot.py` — optional renderer (matplotlib) that
  loads a benchmark CSV and produces a `(closure, memory)` scatter
  plot with quadrant labels. Available via `pip install
  autonometrics[viz]`; the package itself remains pure-`numpy`.
- `docs/benchmarks/v0.5.0a0.csv` — snapshot of the benchmark run
  shipped with this release: 69 configurations, 48 valid points
  (the other 21 degenerate to `H(S_{t+1}|E_t) = 0` and are flagged
  per row).
- `docs/benchmarks/v0.5.0a0.png` — scatter rendering of the same
  CSV.
- `docs/benchmarks/v0.5.0a0.log.txt` — captured stdout of the
  reference run, kept for traceability of the headline numbers.
- `viz` extra in `pyproject.toml`: `matplotlib>=3.7`, only required
  for the optional plotting script.

### Notes on the benchmark run

For the systems and parameter sweeps shipped here:

- Sample: 48 valid `(closure, memory)` points out of 69 configurations
  (21 degenerate to a constant focal trajectory and are excluded;
  this is a property of the specific systems, not of the metrics).
- Pearson r(closure, memory) = +0.3193.
- Spearman r(closure, memory) = +0.5589.
- Both values are below the `|r| < 0.7` falsification threshold from
  `docs/PBA.md`, so on this zoo the two axes carry distinct
  information and adding a third PBA-shaped axis remains motivated.
- The Spearman value (≈ 0.56) is moderate, not low, and is partly
  inflated by a saturation cluster at `closure = 1.0`: every ECA
  configuration with non-zero conditional variability lands on that
  vertical wall by construction (the focal cell is fully determined
  by `(S_t, E_t)`), and the periodic / self-generated systems also
  collapse to `(1, ≈0.97)`. This is a property of the current
  adapter zoo, not of the metric pair, and is documented as a known
  limitation rather than a finding about autonomy.

### Changed

- README, `docs/PBA.md`, `docs/PBA.es.md`: corrected the attribution
  of the fifth roadmap axis. The "general constrained dynamics"
  formalisation is from Montévil & Mossio (2015), *Biological
  Organisation as Closure of Constraints* (J. Theor. Biol.), not
  from Farnsworth. The roadmap entry now reads "constraint-closure
  ratio (Montévil & Mossio-style)".
- README "Theoretical grounding" entry for Farnsworth (2018) now
  states the dual-feature thesis correctly: organisational closure
  + an internalised objective-function (a 'goal'), with Integrated
  Information Theory proposed as a possible quantification. The
  previous entry mis-summarised it as "closure and memory-bearing
  structure", which collapsed two distinct levels of Farnsworth's
  scheme. The entry now also clarifies that the package's `(closure,
  memory)` plane is *inspired by*, not a literal implementation of,
  the Farnsworth thesis: the memory ratio is a structural proxy for
  ongoing activity, not an objective-function measurement.
- Roadmap reordered. The `v0.5.0-alpha` slot, previously announced
  for the third (RAI) axis, is now occupied by the benchmark suite
  shipped here. The third, fourth and fifth axes shift to
  `v0.6.0-alpha`, `v0.7.0-alpha` and `v0.8.0-alpha` respectively.
  The decision is documented inline: validating that the existing
  two axes carry distinct information has to come before adding a
  third one, otherwise PBA accumulates redundant axes without
  evidence.

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
