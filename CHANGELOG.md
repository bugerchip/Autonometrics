# Changelog

All notable changes to `autonometrics` are documented in this file.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [PEP 440](https://peps.python.org/pep-0440/)
version numbering. Until the first non-alpha release every minor
version may introduce breaking changes.

## [0.7.2a0] - 2026-05-02

> Maintenance and analysis cycle. **No new metric, no API
> change.** Version `0.7.1a0` is *intentionally skipped* and
> reserved for the persistence-boundary theorem cycle (see
> `docs/PBA.md` *Next decision points* and `docs/RAI.md` open
> design questions). Skipping a sub-version this way keeps the
> `0.7.x` series chronologically auditable: `0.7.0a0` shipped
> the metric and the diagnostic, `0.7.1a0` will formalise its
> boundaries, `0.7.2a0` (this release) ships the geometric audit
> of the four-axis cloud.

### Added

- **Pre-registered atlas-geometry analysis cycle.** New design
  document `docs/ATLAS_GEOMETRY.md` locks the research
  question (Level 2 vs Level 3 unification of PBA), the
  techniques (PCA primary, k-means + silhouette secondary,
  t-SNE/UMAP illustrative-only), the numerical thresholds
  anchored in Jolliffe (2002) and Rousseeuw (1987), the
  treatment of dropouts, and the documentation structure
  *before* the analysis is run. Three predicted outcomes
  (Level 2 reinforced, inconclusive, Level 3 suspected) are
  enumerated in advance so the verdict cannot drift after the
  data is in.
- **Extended four-axis benchmark snapshot
  `docs/benchmarks/v0.7.2a0.{csv,png,log.txt}`.** Same zoo as
  `v0.7.0a0` but with `n_seeds` raised from 5 to 30 (typical
  guideline of 5 → 20 was insufficient because retention is
  ~60%; 30 clears the pre-registered floor of 200 valid points
  with margin). 247 valid points out of 405 swept
  configurations. All six pairwise `|Pearson r| < 0.7` —
  closure–memory `+0.27`, closure–constraint `+0.04`,
  closure–persistence `−0.61`, memory–constraint `−0.52`,
  memory–persistence `−0.33`, constraint–persistence `−0.07`.
  The `v0.7.0a0` falsification result therefore survives the
  larger sample.
- **`examples/atlas_geometry.py`.** numpy-only analyser that
  computes:
  - PCA via `numpy.linalg.svd` on the standardised 4-D matrix
    (per-component variance shares and cumulative ratios),
  - k-means with k-means++ initialisation and 20 restarts on
    the PCA-whitened scores for `k ∈ {2, 3, 4, 5}`,
  - silhouette score (Rousseeuw 1987) per `k`,
  - cluster composition by adapter class at `k* =
    argmax_k s(k)`,
  - conditional Pearson correlations within each cluster and
    within each adapter class (Simpson's-paradox check),
  - dropout breakdown by adapter class and by parameter
    setting.
  Output: human-readable stdout, structured JSON snapshot at
  `docs/benchmarks/atlas_geometry_v0.7.2a0.json`. The script is
  threshold-free; thresholds live in
  `docs/ATLAS_GEOMETRY.md` and verdict prose in `docs/PBA.md`.
- **`examples/atlas_geometry_plot.py`.** Two-panel matplotlib
  figure: a scree plot with the pre-registered `λ_1 ≥ 0.70`
  reference line and the cumulative variance overlay, plus a
  PC1 vs PC2 biplot with axis loadings drawn as labelled
  arrows, points coloured by k-means cluster and shape-coded
  by adapter class. Snapshot at
  `docs/benchmarks/atlas_geometry_v0.7.2a0.png`. t-SNE/UMAP
  panels are deliberately omitted per the pre-registration's
  "illustrative only, not evidence" clause.
- **Tests:** `tests/benchmarks/test_atlas_geometry_smoke.py` (7
  tests covering PCA recovery on synthetic anisotropic data,
  k-means separation of well-separated blobs, silhouette
  sensitivity to label quality, CSV round-trip and JSON write
  on the v0.7.2a0 snapshot, dropout-breakdown consistency) and
  `tests/benchmarks/test_atlas_geometry_plot_smoke.py` (2
  tests covering JSON load and PNG render round-trip).
- **Verdict (atlas-geometry analysis).** Inconclusive on the
  level question (PCA reading), with a Level-3-suggestive
  overlay (clustering reading). Indicators on the v0.7.2a0
  zoo: `λ_1 = 0.469` (in pre-registered inconclusive band),
  `λ_1 + λ_2 = 0.809` (in pre-registered partial-low-D band),
  `s(k* = 5) = 0.642` (above pre-registered Outcome-B
  ceiling), 4 of 5 k-means clusters dominated by a single
  adapter class. The combination is not a clean fit to any of
  the three pre-registered outcomes; the verdict resolves the
  gap by treating PCA as primary (per Decision 2) and the
  substrate-aligned clusters as a Level-3-suggestive overlay.
  Documentation around the four-axis conjunction moves from
  "Level 2 plausible" to "Level 2 plausible on the structural
  geometry, but the cluster overlay is L3-suggestive on the
  same data; the question is genuinely under-determined and is
  pushed to v0.9.0".
- **Simpson's-paradox health flag raised.** Several global
  pairwise correlations are partly artefacts of the substrate
  composition of the zoo. The most extreme case:
  closure–persistence global `−0.61`, within `KauffmanNetwork`
  `−0.07`, within `SimpleAutomaton` `−1.00`. The flag is *not*
  a level-question decision (per Decision 3 it is a health
  flag), but it reinforces the L3-suggestive overlay above.
- **Dropout pattern documented as a structural finding.** The
  extended sweep produces a 39% dropout rate concentrated on
  `ECASystem` (55%) and `KauffmanNetwork` (51%) and zero on
  `PeriodicCycle` and `SimpleAutomaton`. The metric set has a
  joint blind spot selective for the cellular and network
  adapters; the verdict is conditional on the
  `non-degeneracy` clause, the same convention already used in
  the saturation and constraint-density theorems.

### Changed

- **Version bump** `0.7.0a0 → 0.7.2a0` in `pyproject.toml`,
  `src/autonometrics/__init__.py`, and `tests/test_smoke.py`.
  `0.7.1a0` is *intentionally skipped* (reserved for
  persistence-boundary theorems and the perturbation-magnitude
  sweep deferred from `v0.7.0a0`).
- **`examples/benchmark_demo.py`** now exposes a `--n-seeds`
  flag (default 30) and `iter_systems` / `run_benchmark` accept
  an `n_seeds` keyword argument. Default snapshot path moved
  from `docs/benchmarks/v0.7.0a0.csv` to
  `docs/benchmarks/v0.7.2a0.csv`. Periodic adapters use
  `max(3, n_seeds // 2)` seeds since they have less stochastic
  structure to exercise.
- **`examples/benchmark_plot.py`** default input/output paths
  moved to `v0.7.2a0.{csv,png}`.
- **`docs/PBA.md` and `docs/PBA.es.md`** gain a new "Atlas
  geometry: do the four axes share a single object?"
  subsection summarising the indicators, the band mapping, and
  the verdict; "Current evidence status" updated to record the
  v0.7.2a0 benchmark and the verdict; "Next decision points"
  updated.
- **`README.md`** roadmap, status, and benchmark sections
  updated to reflect `v0.7.2a0`.

### Skipped versions

- **`0.7.1a0`** (intentionally reserved). Will land:
  - Theorem statements for the two persistence-boundary
    regimes observed in the `v0.7.0a0` U-shape diagnostic
    (low-coupling fixed-point absorption,
    high-coupling perturbation invisibility),
  - Perturbation-magnitude sweep for `rai_proxy_persistence`
    deferred from the `v0.7.0a0` design questions in
    `docs/RAI.md`.

## [0.7.0a0] - 2026-05-02

### Added

- **Fourth PBA axis: `rai_proxy_persistence` (Lee & McShea-style
  perturbation persistence).** Operationalises a structural
  autonomous-motivation proxy (RAI-style) on the existing adapter
  zoo. The score answers "if the system is perturbed, does it
  return to its own trajectory?" via:
  ```
  persistence = clip(1 − d_bar / d_ref, 0, 1)
  ```
  where `d_bar` is the mean Hamming distance between the perturbed
  and the unperturbed focal trajectories over a horizon of
  `horizon` steps (default 64), averaged over `n_perturbations`
  independent perturbation times (default 32), and `d_ref =
  1 − Σ p_a²` is the empirical complement of the collision
  probability of two i.i.d. draws from the focal marginal. The
  metric lands in `[0, 1]`: `1.0` means perturbations are absorbed
  perfectly; `0.0` means perturbations propagate as much as
  random noise of the same alphabet.
- **Provenance and adaptation explicit.** The metric is a
  generalisation of Lee & McShea (2020) *persistence* to systems
  without an externally specified goal. Four adaptations vs the
  original formula are documented in `src/autonometrics/metrics/
  persistence.py` and in `docs/RAI.md`: implicit goal (the
  system's own unperturbed trajectory), Hamming distance for
  discrete state, empirical baseline `R` per adapter, and
  multi-perturbation averaging.
- **Independence-by-design audit baked into the module.**
  `compute_rai_proxy_persistence` does not import any of
  `_entropy`, `albantakis`, `memory_ratio`,
  `constraint_closure` or third-party information-theory toolkits.
  An automated test asserts the no-cross-import contract, so the
  audit cannot silently regress.
- **Adapter-side replay protocol.** All deterministic adapters in
  the zoo (`ECASystem`, `KauffmanNetwork`, `SimpleAutomaton`,
  `PeriodicCycle`) now expose `replay_from_perturbation(t_star,
  n_steps, rng=None)`, which returns the focal trajectory after a
  single-element perturbation has been applied to the system's
  full internal state at time `t_star`. CSV-only adapters
  (`CSVTrajectory`) deliberately do *not* implement the method,
  and `Autonometer` records `None` for the persistence axis on
  those adapters — the same fail-loudly contract used for
  `get_causal_graph` and the constraint-closure axis.
- **`Autonometer` now dispatches a third input kind.** A new
  `_INPUT_REPLAY` kind is added alongside `_INPUT_TRAJECTORY` and
  `_INPUT_GRAPH`. `AutonomyProfile` gains a fourth field,
  `rai_proxy_persistence: float | None`, with a docstring that
  flags it as a *structural proxy*: strong validation against
  transcript-based RAI scoring is deferred to `v0.9.0` (per
  `docs/RAI.md`).
- **Mini-benchmark expanded to four axes and six pairwise
  correlations.** `examples/benchmark_demo.py` now measures
  `(closure, memory, constraint, persistence)` per system and
  reports the full six-pair correlation matrix. The on-stdout
  table and the written CSV both gain a `persistence` column.
  Snapshot at `docs/benchmarks/v0.7.0a0.{csv,png,log.txt}`.
- **Empirical falsification gate passed.** Aggregate diagnosis on
  the full v0.7.0a0 zoo (48 fully-valid points) is `OK`: every
  pairwise `|r| < 0.7`. The three new pairs involving the
  persistence axis sit comfortably below the threshold:
  - `closure-persistence`: `pearson −0.4386, spearman −0.5022`
  - `memory-persistence`: `pearson −0.3776, spearman −0.4164`
  - `constraint-persistence`: `pearson +0.0461, spearman +0.2080`
  This is the empirical correlation threshold pre-registered in
  `docs/RAI.md` ("Empirical correlation `|r| < 0.7` on the
  benchmark zoo"). The atlas of autonomy gains a fourth axis
  that survives the audit both structurally (no shared imports
  with the other three) and empirically (low pairwise
  correlations).
- **Persistence diagnostic + plot.** `examples/persistence_
  diagnostic.py` sweeps the focal coupling of `KauffmanNetwork`
  from `0.0` to `1.0` and reports a per-coupling `mean ± std`.
  `examples/persistence_plot.py` renders the curve with
  `matplotlib`. Snapshot at
  `docs/benchmarks/persistence_v0.7.0.{csv,png,log.txt}`.
- **U-shape boundary regimes recorded as a finding.** The
  diagnostic *falsified* the naïve "monotone rise from low to
  high persistence as coupling grows" expectation. The actual
  shape is U-shaped:
  ```
  coupling=0.00 -> persistence = 1.000 (n=6/10 valid)  [trivial absorption: focal collapses to fixed point]
  coupling=0.60 -> persistence = 0.415 (n=9/10 valid)  [non-trivial middle]
  coupling=1.00 -> persistence = 0.665 (n=9/10 valid)  [trivial absorption: focal flip invisible]
  ```
  Two boundary regimes produce trivial-absorption signatures of
  different kinds, and the meaningful useful range of the metric
  on Kauffman networks lies in the intermediate couplings.
  Formalising the two theorems is the planned content of the
  `v0.7.1` maintenance cycle, jointly with the
  perturbation-magnitude sweep already deferred there in
  `docs/RAI.md`.
- **Tests.** 16 new tests covering: the four adapter replay
  methods (8 tests), the `Autonometer` four-axis combo and the
  None-fallback for replay-less adapters (3 tests), the
  diagnostic sweep, CSV format, aggregate grouping and the
  diagnosis-line `[OK]` U-shape verdict (5 tests), the plot's
  CSV loading, aggregate grouping and PNG rendering (3 tests).
  Plus 10 unit tests for the metric proper covering the full
  score range, all input-validation paths, and the
  no-cross-import audit. Total suite is now 212 tests (up from
  196 at `v0.6.1a0`); all green.

### Changed

- Version bumped from `0.6.1a0` to `0.7.0a0` across
  `pyproject.toml`, `src/autonometrics/__init__.py`, and
  `tests/test_smoke.py`.
- `examples/benchmark_plot.py` defaults updated to the
  `v0.7.0a0` CSV / PNG paths. The scatter still uses the
  `(closure, memory)` plane plus `constraint` as marker size for
  visual continuity; the persistence axis appears in its own
  diagnostic plot rather than as a fourth visual encoding on the
  scatter.
- The `AutonomySystem` protocol docstring documents the new
  optional `replay_from_perturbation` method (with the same
  opt-in style used for `get_causal_graph`), formalising the
  contract that replay-less adapters return `None` rather than
  failing.

### Why this release exists

`v0.7.0a0` ships the metric drawn up by the design document
introduced in the previous commit (`docs/RAI.md`) — the fourth
PBA axis. Three things make the release defensible enough to be
worth tagging:

1. **Lineage.** The metric is not invented from scratch but
   adapted from Lee & McShea (2020). Four explicit adaptations
   are documented; both halves (their intuition + our
   discrete-state generalisation) are cited in code, in the
   metric's docstring, and in `docs/RAI.md`.
2. **Independence.** Static (no-cross-import) and empirical
   (`|r| < 0.7`) audits both pass. The atlas claim survives.
3. **Honest diagnostic.** The persistence diagnostic *falsified*
   its own naïve expectation and revealed two trivial-absorption
   boundary regimes. We documented the U-shape rather than
   smoothing it away. The boundary theorems are explicitly
   deferred to `v0.7.1`, mirroring the maintenance cadence
   already established by `v0.5.1a0` (closure saturation) and
   `v0.6.1a0` (constraint-closure density).

The cross-tradition test of the atlas hypothesis is partial at
this point: the structural proxy passes the structural audit on
the existing zoo, but the strong validation against behavioural
RAI on transcript adapters is still deferred to `v0.9.0`. The
release reports this gap explicitly in `docs/PBA.md` and in
`AutonomyProfile.rai_proxy_persistence`'s docstring.

## [0.6.1a0] - 2026-05-02

### Added

- **Domain-of-applicability diagnostic for the constraint-closure
  axis.** Mirrors the closure-saturation diagnostic shipped in
  `v0.5.1a0` and formalises the two boundary regions of
  `compute_constraint_closure`:
  - **Theorem A — single-constraint trivial-zero.** Any system
    with `n = 1` update function returns `0.0` by construction
    (a simple cycle of length 2 or 3 requires at least two
    distinct nodes). Covers `PeriodicCycle` and
    `SimpleAutomaton`.
  - **Theorem B — symmetric-neighbour saturation.** Any graph
    in which every node reads at least one node that reads it
    back returns `1.0` by construction (every node sits on a
    length-2 cycle). Covers `ECASystem` on any non-trivial
    periodic ring.
- `examples/constraint_density_diagnostic.py` — sweeps
  `KauffmanNetwork` with `K ∈ {1, …, n−1}` over independent
  seeds and computes `constraint_closure` directly from the
  causal graph (no trajectory needed; the metric is purely
  topological). Reports a per-row table, a CSV under
  `docs/benchmarks/`, an aggregate `mean ± std` table, and a
  diagnosis line that flags whether the curve walks
  monotonically from the lower boundary to the upper one.
  Supports `--quick` for CI smoke and `--n-nodes` /
  `--n-seeds` for custom sweeps. Numpy-only.
- `examples/constraint_density_plot.py` — optional matplotlib
  renderer that turns the diagnostic CSV into a
  `constraint_closure` vs `K` curve with `mean ± std` error
  bars. Auto-titled with the first/last density points so a
  glance at the figure conveys the curve shape. Behind the
  `autonometrics[viz]` extra; the rest of the package stays
  matplotlib-free.
- `docs/benchmarks/constraint_density_v0.6.1.{csv,png,log.txt}`
  snapshot from the full default sweep (n=10, 9 K values, 10
  seeds, 90 measurements). The mean curve walks
  `0.140 ± 0.120 → 0.520 ± 0.236 → 0.790 ± 0.138 → 0.950 ± 0.067 → 0.980 ± 0.060 → 1.000 ± 0.000`
  (`K = 1, 2, 3, 4, 5, ≥6`), with `std = 0` from `K = 6`
  upward (every seed identically saturates). Both boundary
  theorems are recovered jointly.
- New "Domain of applicability (added in v0.6.1a0)" section in
  `docs/CONSTRAINT_CLOSURE.md`. States the two theorems with
  their proofs, references the diagnostic snapshot, and spells
  out the two practical consequences for downstream
  interpretation: single-node adapters are not measurement
  failures (they sit outside the metric's discriminative
  domain), and dense-and-symmetric adapters saturate identically
  (so distinguishing rule 30 from rule 110 has to come from
  other axes).
- `docs/PBA.md` and `docs/PBA.es.md` "Constraint-closure
  complements the wall, not replaces it" subsection extended
  with the formal Theorem A / Theorem B statements and a link
  to the new diagnostic snapshot.
- `tests/benchmarks/test_constraint_density_smoke.py` — 9
  smoke tests covering the default and quick `K` schedules,
  the lower-boundary cluster at `K = 1`, the upper-boundary
  saturation at `K = n − 1`, the rise across the curve, the
  CSV writer schema, the aggregate grouping, and the
  diagnosis-line `[OK]` verdict on the full sweep.
- `tests/benchmarks/test_constraint_density_plot_smoke.py` — 4
  smoke tests behind `pytest.importorskip("matplotlib")`
  covering CSV coercion, per-K aggregation, PNG rendering,
  and the empty-CSV failure path.

### Changed

- Version bumped from `0.6.0a0` to `0.6.1a0` across
  `pyproject.toml`, `src/autonometrics/__init__.py`, and
  `tests/test_smoke.py`.

### Why this release exists

The `v0.6.0a0` benchmark introduced the third axis, broke the
closure-saturation wall, and pushed PBA from "two-axis working
hypothesis" to "three-axis working hypothesis with empirically
distinguishable axes". It also surfaced a question it could not
itself answer: where does the new axis become uninformative?
The honest reading of `v0.6.0a0` is that single-node adapters
land at `constraint = 0.0` and ECA rings land at
`constraint = 1.0`, but those are observations on a fixed zoo,
not theorems. `v0.6.1a0` upgrades them to theorems, verifies
the joint shape on a controllable Kauffman sweep, and lifts the
domain-of-applicability discussion to the same level of rigour
that the closure axis already enjoys after `v0.5.1a0`. The
release is intentionally small and is shipped before the next
axis (RAI) so the PBA atlas grows with documented edges, not
with implicit ones.

## [0.6.0a0] - 2026-05-01

### Added

- Third PBA axis: **constraint-closure** (Montévil & Mossio).
  `src/autonometrics/metrics/constraint_closure.py` implements
  `compute_constraint_closure(causal_graph)`, returning a ratio in
  `[0, 1]`: the fraction of a system's update-function nodes that
  lie on at least one simple directed cycle of length 2 or 3 in
  the causal-dependency graph. Self-loops do not count, and cycles
  of length 4 or longer are excluded by design so that systems on
  globally-cyclic boundary conditions (e.g. periodic ECA rings)
  are not awarded a free pass on closure they did not earn
  organisationally.
- `AutonomyProfile.constraint_closure: float | None` field.
- `Autonometer` now dispatches three metric inputs: trajectories
  for `albantakis` and `memory`, and a causal graph for
  `constraint_closure`. Adapters that do not implement
  `get_causal_graph()` (or that raise `NotImplementedError`) make
  the orchestrator record `None` for that field rather than
  abort the whole measurement, so the public API stays
  backwards compatible for `CSVTrajectory`-style inputs.
- `get_causal_graph()` implementations on every adapter shipped
  with the package: `ECASystem` (periodic three-neighbour ring),
  `KauffmanNetwork` (one row per node from `_inputs`),
  `PeriodicCycle` (single self-loop), `SimpleAutomaton`
  (single node, with or without a self-loop depending on
  mode).
- `docs/CONSTRAINT_CLOSURE.md` — detailed design document for
  the new axis. Spells out the operationalisation choices
  (constraint = update function, dependency = topological,
  closure counted only on simple cycles of length 2 or 3),
  per-adapter predictions with falsification thresholds, the
  pre-implementation review that motivated the
  short-cycle restriction, and an
  independence-by-design guarantee against information-theoretic
  imports.
- `tests/test_constraint_closure.py` — 15 canonical-graph tests
  pinning the metric on small graphs (single node, mutual pair,
  triangle, chain, complete graph, partial closure, length-4
  cycle alone, and the input-validation paths). Includes a
  static audit that re-reads the metric module and asserts it
  imports neither `_entropy` nor any of the existing metric
  modules.
- `tests/test_constraint_closure_adapters.py` — 19 adapter-level
  tests checking that each adapter's `get_causal_graph()` agrees
  with the design predictions, that the metric scores on each
  adapter fall in the expected ranges (ECA = 1.0, Periodic and
  SimpleAutomaton = 0.0, Kauffman K=1 low / K=3 high), and that
  the orchestrator returns `None` instead of aborting on
  graph-less adapters.
- `examples/benchmark_demo.py` — extended to three axes and
  three pairwise correlations
  (`closure-memory`, `closure-constraint`,
  `memory-constraint`). The aggregate diagnosis flag is now the
  worst of the three pairwise flags so a single overlap raises
  it.
- `examples/benchmark_plot.py` — encodes the `constraint` axis
  as marker size on the existing 2-D scatter. Falls back to a
  uniform marker size when the input CSV has no
  `constraint` column, so older snapshots keep rendering
  unchanged.
- `docs/benchmarks/v0.6.0a0.csv`,
  `docs/benchmarks/v0.6.0a0.png`,
  `docs/benchmarks/v0.6.0a0.log.txt` — snapshot of the
  three-axis run shipped with this release.

### Notes on the benchmark run

For the systems and parameter sweeps shipped here:

- Sample: 48 fully-valid `(closure, memory, constraint)` points
  out of 69 configurations (21 degenerate to a constant focal
  trajectory and are excluded).
- Pairwise Pearson correlations:
  `r(closure, memory) = +0.3193`,
  `r(closure, constraint) = -0.0425`,
  `r(memory, constraint) = -0.5675`.
- Pairwise Spearman correlations:
  `r(closure, memory) = +0.5589`,
  `r(closure, constraint) = -0.2736`,
  `r(memory, constraint) = -0.4458`.
- All three Pearson values are below the `|r| < 0.7`
  falsification threshold from `docs/PBA.md`. The aggregate
  diagnostic flag is `OK`. The three axes therefore carry
  distinct information on the current adapter zoo, and adding
  the fourth axis remains motivated.
- The third axis breaks the `closure = 1.0` saturation wall
  identified in `v0.5.0a0` and characterised in `v0.5.1a0`.
  Single-node periodic cycles and self-generated automata,
  which previously sat indistinguishably with the ECA rings on
  that wall, now drop cleanly to `constraint = 0.0` while ECA
  rings stay at `constraint = 1.0`. The wall is therefore not
  resolved (closure still saturates by construction in
  fully-observed deterministic systems) but the wall is no
  longer the only readable signal.

### Changed

- `_METRIC_REGISTRY` and `Autonometer.measure` now route metrics
  by input kind (trajectory vs causal graph). The dispatch is
  internal; user code that calls `Autonometer.measure(system)`
  is unaffected.
- `docs/PBA.md` and `docs/PBA.es.md`: new section "What kind of
  unification PBA proposes" / "Qué tipo de unificación propone
  PBA" formalising the multidimensional-atlas framing surfaced
  by the v0.6 benchmark results. PBA is positioned as a
  **Level 2** unification (shared structure with multiple
  coordinates, like color, Big Five personality, or temperature
  before the kinetic theory) rather than a **Level 1**
  unification (extensional identity, entropy-style). The Level 1
  reading is recorded as already-falsified by the observed
  pairwise correlations of `+0.32`, `-0.04` and `-0.57`; the
  Level 2 reading is what the package actually claims and what
  the benchmarks test. The phrase "atlas of autonomy" is
  introduced as the canonical one-line description.
- `docs/PBA.md` and `docs/PBA.es.md`: "Domain of applicability"
  now records that the third axis complements the wall rather
  than replacing it (`closure = 1.0` saturation for
  fully-observed deterministic systems is still a theorem of
  the metric, but `constraint_closure` separates single-node
  systems from networked ones inside that wall). "Current
  evidence status" and "Next decision points" updated to
  reflect three axes implemented and the v0.6 benchmark
  results.
- `README.md` opening paragraph reframes the PBA pitch around
  the atlas-of-autonomy framing instead of suggesting an
  entropy-style reduction.
- `pyproject.toml` and `src/autonometrics/__init__.py` bumped
  to `0.6.0a0`.
- Public API re-export: `compute_constraint_closure` is now
  available from the top-level `autonometrics` namespace.

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
