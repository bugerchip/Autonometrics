# autonometrics

> ### *Shadows of Self-Determination*
>
> **An instrument for quantifying structural self-determination across systems.**
>
> *We see shadows of autonomy, calibrated and reproducible.*
> *Whether the cave behind them holds one object or many,*
> *this tool does not decide.*

**Status:** `alpha` — work in progress, API unstable.

---

## What it is

`autonometrics` is a Python instrument that takes a discrete
trajectory — a cellular automaton, a Boolean network, an agent
log, a simulation, and as of `v0.8.0a0` also a system that
publishes its own *intended* trajectory alongside its realised
one — and returns up to **five normalised readings** of how
*self-determined* its structure looks. Each reading comes from
a different scientific tradition; together they form a small
**atlas of autonomy**: a few charts that cover the same
territory from different operational angles.

It is a measurement tool, not a new theory of autonomy. The
package collects existing measures, normalises them to a
shared `[0, 1]` scale, and lets you compare points from very
different substrates in the same space.

## The five axes

| Axis | Question it answers | Tradition | Reference |
|---|---|---|---|
| **`closure`** | How much of the system's information is generated *from inside*? | Information theory | Shannon (1948); Bertschinger et al. (2008); Albantakis (2021) |
| **`memory`** | How much of the system's predictability is carried *by its own past*? | Computational mechanics | Crutchfield & Young (1989); Feldman & Crutchfield (2002) |
| **`constraint`** | How tightly do the system's constraints enable *each other*? | Theoretical biology | Montévil & Mossio (2015) |
| **`persistence`** | How well does the system's structure resist a small perturbation? | Operational goal-directedness | Lee & McShea (2020) |
| **`coherence`** | How well does the system's *executed* trajectory follow its *declared* one? | Akrasia → cognitive dissonance → AI alignment | Festinger (1957); Sheeran (2002); Lanham (2023); Turpin (2023) |

All five readings live in `[0, 1]` and can be plotted,
correlated and compared across substrates that expose the
relevant capability. The first four require only a state /
environment trajectory; the fifth additionally requires a
parallel `(declared, executed)` pair, which only adapters
with an explicit declarative layer expose. Adapters that do
not implement that layer report `coherence = None` honestly,
in line with the same dropout policy already used for
`constraint_closure` (graph-only) and `persistence`
(replay-only).

## What the project does *not* claim

The five axes are **not** assumed to be shadows of a single
underlying quantity. The current empirical picture
(`v0.8.0a0`, 645-point synthetic benchmark) is honest about
that:

- All four `v0.7.x` pairwise correlations remain below
  `|r| < 0.7` on every sub-zoo where they are jointly
  defined, so the four prior axes still carry distinct
  information.
- The fifth axis (`coherence`) is empirically distinct from
  the first four under controlled adapters: when the
  `PromisedCycle` reference adapter is driven by **two
  independent sources of variability** rather than one,
  `r(closure, coherence)` falls from `+0.97` to `+0.48` and
  `r(coherence, p_env) ≈ 0` confirms the formula's predicted
  invariance to declarative-side noise. Details and
  pre-registered analysis in [`docs/CBA.md`](docs/CBA.md)
  and the diagnostic snapshots under `docs/benchmarks/`.
- The full five-axis cloud **does not exist on the current
  zoo**: each adapter class implements either
  `get_causal_graph` (so `constraint_closure` is defined)
  or `get_declared_executed` (so `coherence` is defined),
  but never both, leaving `n_valid_full = 0/645`. The atlas
  is therefore best read as a **mosaic / archipelago** of
  overlapping four-axis sub-charts rather than a single
  five-dimensional cloud. The verdict is documented in the
  v0.8.0a0 follow-up of
  [`docs/ATLAS_GEOMETRY.md`](docs/ATLAS_GEOMETRY.md).

So the package ships a measurement framework, a benchmark,
the dropouts, and a falsifiable working hypothesis — not a
definitive theory of autonomy. The level question (one
object or many?) is **pulled toward Level 3 (mosaic) by the
v0.8.0a0 cycle but not yet decided**; the strong validation
against behavioural / RAI-style data is deferred to v0.9.0,
which is also the natural candidate for a substrate that
finally closes the five-axis hole.

The full conceptual statement and the falsification
criteria live in [`docs/PBA.md`](docs/PBA.md) (English) and
[`docs/PBA.es.md`](docs/PBA.es.md) (Spanish). The
pre-registered geometry analysis is in
[`docs/ATLAS_GEOMETRY.md`](docs/ATLAS_GEOMETRY.md); per-axis
design notes in
[`docs/CONSTRAINT_CLOSURE.md`](docs/CONSTRAINT_CLOSURE.md),
[`docs/RAI.md`](docs/RAI.md) and
[`docs/CBA.md`](docs/CBA.md). The release log lives in
[`CHANGELOG.md`](CHANGELOG.md).

## Installation

### From PyPI (recommended)

```bash
pip install --pre autonometrics
```

For the optional plotting / benchmark dependencies:

```bash
pip install --pre "autonometrics[viz]"
```

> The `--pre` flag is required while the package is in `alpha`.
> Once a non-alpha release is published, plain `pip install
> autonometrics` will be enough.

### From source (for development)

```bash
git clone https://github.com/bugerchip/Autonometrics.git
cd Autonometrics
pip install -e ".[dev,viz]"
```

Requires Python 3.10 or later. The core package depends only on
`numpy`. The optional `viz` extra adds `matplotlib`, used by the
benchmark plotting scripts.

## Quickstart

### One-line measurement (recommended)

Since `v0.8.1a0` the package exposes the canonical axis names
(`closure`, `memory`, `constraint`, `persistence`, `coherence`) and a
top-level `measure()` helper. The shortest possible end-to-end
measurement reads:

```python
import autonometrics as anm

system = anm.PromisedCycle(length=600, period=4, alphabet=4, p_noise=0.1)
profile = anm.measure(system)

print(profile)
print(profile.to_dict())
print(profile.defined_axes())
```

`anm.measure(system)` defaults to all five canonical axes. Axes the
adapter does not support are reported as `None` (mosaic-dropout
policy) instead of aborting the measurement.

### Asking for a subset of axes

```python
import autonometrics as anm

profile = anm.measure(system, axes=["closure", "coherence"])
print(profile["closure"], profile["coherence"])
```

The full list of canonical axis names lives in `anm.AXES`:

```python
>>> anm.AXES
('closure', 'memory', 'constraint', 'persistence', 'coherence')
```

### Measuring a synthetic automaton

```python
import numpy as np
import autonometrics as anm

rng = np.random.default_rng(0)
env = rng.integers(0, 3, size=3000).astype(np.int64)

system_a = anm.SimpleAutomaton.from_self_generated_rules(n_states=4, env=env, seed=0)
system_b = anm.SimpleAutomaton.from_external_rules(n_states=4, env=env, seed=0)

profile_a = anm.measure(system_a, axes=["closure", "memory"])
profile_b = anm.measure(system_b, axes=["closure", "memory"])

print(profile_a.closure, profile_a.memory)
print(profile_b.closure, profile_b.memory)
```

### Measuring a CSV trajectory you already have

```python
import autonometrics as anm

trajectory = anm.CSVTrajectory.from_path("my_log.csv")  # header: state,env
profile = anm.measure(trajectory, axes=["closure", "memory"])
```

`my_log.csv` is a two-column file with discrete integer labels:

```
state,env
0,1
2,1
2,0
1,0
```

### Running the bundled demos

```bash
python examples/automaton_demo.py   # clockwork vs mixed vs noise-driven automata
python examples/csv_demo.py         # round-trip through a CSV file
```

## Metrics

Three metrics ship in the current alpha. All three follow the PBA
*internal over total* shape, all three live in `[0.0, 1.0]`, and all
three are exposed as pure `numpy` functions wired into `Autonometer`:

### `ratio_endo_total` — Albantakis / Bertschinger closure

Normalised conditional mutual information of the system's next state
on its own past, controlling for the environment:

$$A \;=\; \frac{I(S_{t+1};\,S_t \mid E_t)}{H(S_{t+1} \mid E_t)}$$

- `A = 0`: the next state, given the environment, is independent of
  the system's own previous state (no closure, pure drift).
- `A = 1`: the next state, given the environment, is fully determined
  by the system's own previous state (closed dynamics).

### `memory_endo_ratio` — distributed structural memory

Fraction of the structural memory present in the joint
`(system, environment)` trajectory that is carried by the system
itself, computed via Crutchfield's excess entropy on each component
and then normalised:

$$M \;=\; \frac{E(\text{states})}{E(\text{states}) + E(\text{env})}$$

with `E(.)` estimated via block-entropy saturation
`E = H(L) - L · h_μ`, where `h_μ = H(L) - H(L-1)`. The working block
length is capped by a Grassberger-style rule so every possible block
gets about ten samples on average.

- `M = 0`: the joint memory lives entirely in the environment (or, by
  convention, neither sequence carries memory at all).
- `M = 1`: the joint memory lives entirely in the system.
- `M ≈ 0.5`: memory is shared roughly equally between system and
  environment.

This replaces the absolute-bit `structural_memory` shipped in
`v0.3.x`. Returning a magnitude in bits broke the unifying *ratio*
shape of the package; `memory_endo_ratio` recovers PBA coherence by
applying the same excess-entropy estimator to both components and
returning the fraction carried by the system.

### `constraint_closure` — Montévil & Mossio-style organisational closure

Fraction of the system's update functions (constraints) that lie on
at least one simple directed cycle of length 2 or 3 in the
causal-dependency graph. The metric reads only the topology of the
graph: it is **deliberately information-theory-free**, so any
empirical correlation with the two axes above is structural rather
than algebraic.

$$C \;=\; \frac{|\\{i : \exists \text{ simple cycle of length } 2 \text{ or } 3 \text{ through } i\\}|}{n}$$

with `n` the number of constraints in the system and the dependency
matrix exposed by each adapter via `get_causal_graph()`.

- `C = 0`: no constraint is sustained by another distinct
  constraint of the same system through a short feedback loop.
  Single-node systems (a periodic cycle, a `SimpleAutomaton`) and
  pure feed-forward chains land here.
- `C = 1`: every constraint is on at least one such loop.
  Periodic-ring cellular automata land here because each cell is
  read by both of its neighbours, which read it back.
- Length-1 cycles (self-loops) and length ≥ 4 cycles do **not**
  count: the metric targets the local "membrane ↔ metabolism" shape
  Montévil & Mossio describe, and the short-cycle restriction
  prevents systems that close only after a long detour from getting
  free credit.

Operationalisation choices, falsification predictions and the
domain-of-applicability discussion live in
[`docs/CONSTRAINT_CLOSURE.md`](docs/CONSTRAINT_CLOSURE.md).

All three scores are returned in a single `AutonomyProfile` with
`Optional[float]` fields, so unrequested metrics stay `None`.
Adapters that cannot expose a causal graph (e.g.
`CSVTrajectory`, where only trajectories are available) make the
orchestrator record `None` for `constraint_closure` rather than
abort the whole measurement.

## The autonomy plane

Thinking of the two metrics together, rather than reducing autonomy
to a single number, gives a richer picture. Both axes share the PBA
ratio shape and live in `[0, 1]`, so `(closure, memory)` defines a
**canonical autonomy plane** `[0, 1] × [0, 1]`. The four quadrants
fall out of a single `0.5` threshold on each axis:

| memory ↓ / closure → | **low closure** (< 0.5)         | **high closure** (≥ 0.5)        |
|----------------------|---------------------------------|---------------------------------|
| **low memory** (< 0.5) | drift (noise-driven)          | clockwork regularity            |
| **high memory** (≥ 0.5)| turbulence / chaos            | candidate autopoietic region    |

- **Drift** (low closure, low memory): the system tracks the
  environment and keeps nothing.
- **Clockwork** (high closure, low memory): determined by its own
  past, but the environment also carries comparable memory; the
  system's contribution to joint memory is modest.
- **Turbulence** (low closure, high memory): the environment shapes
  the system, and the bulk of the joint memory still ends up
  associated with the system's trajectory rather than the
  environment's — long-range but non-self-generated structure.
- **Autopoietic region** (high closure, high memory): closed
  dynamics *and* the joint memory is dominated by the system
  itself — the empirically interesting corner for systems with
  non-trivial self-organisation.

The package does not claim to *prove* autopoiesis. It gives a
two-coordinate reading on a homogeneous plane and lets the
interpreter argue.

## Benchmark

`v0.5.0a0` shipped the first reference benchmark on two axes;
`v0.6.0a0` extended it to the third axis (`constraint_closure`);
`v0.7.0a0` added the fourth axis (`rai_proxy_persistence`)
without changing the system zoo. `v0.7.2a0` (this release)
re-runs the four-axis benchmark with `n_seeds` raised from 5 to
30 to clear the 200-valid-point floor pre-registered in
[`docs/ATLAS_GEOMETRY.md`](docs/ATLAS_GEOMETRY.md) for the
atlas-geometry analysis. Adapter classes and parameter values
are unchanged, so all results are directly comparable with the
two prior baselines. The intent is not to score one system as
"more autonomous" than another. It is to check whether the four
axes carry distinct information for the systems we can generate
today, before adding a fifth axis to PBA.

Reproducing the run:

```bash
pip install -e ".[dev]"
python examples/benchmark_demo.py        # writes docs/benchmarks/v0.7.2a0.csv
pip install -e ".[dev,viz]"
python examples/benchmark_plot.py        # writes docs/benchmarks/v0.7.2a0.png
```

Headline numbers from the snapshot shipped here
(`docs/benchmarks/v0.7.2a0.csv`):

| Quantity                              | Value         |
|---------------------------------------|---------------|
| Configurations swept                  | 405           |
| Fully-valid points                    | 247           |
| Configurations dropped (n/a)          | 158 (39%)     |
| Pearson r(closure, memory)            | +0.27         |
| Pearson r(closure, constraint)        | +0.04         |
| Pearson r(closure, persistence)       | -0.61         |
| Pearson r(memory, constraint)         | -0.52         |
| Pearson r(memory, persistence)        | -0.33         |
| Pearson r(constraint, persistence)    | -0.07         |
| Spearman r(closure, memory)           | +0.47         |
| Spearman r(closure, constraint)       | -0.20         |
| Spearman r(closure, persistence)      | -0.47         |
| Spearman r(memory, constraint)        | -0.34         |
| Spearman r(memory, persistence)       | -0.33         |
| Spearman r(constraint, persistence)   | -0.01         |
| Falsification threshold               | `|r| < 0.7`   |
| Aggregate diagnosis                   | OK            |

The 158 dropped configurations correspond to systems whose focal
trajectory collapses to a constant or to a value fully determined
by the environment, in which case `H(S_{t+1} | E_t) = 0` and the
closure ratio is undefined by construction. They concentrate
on `ECASystem` (55% adapter-internal dropout) and
`KauffmanNetwork` (51%); `PeriodicCycle` and `SimpleAutomaton`
have zero dropouts. The pattern is itself a structural finding —
the metric set has a joint blind spot selective for the cellular
and network adapters — and is documented in
[`docs/ATLAS_GEOMETRY.md`](docs/ATLAS_GEOMETRY.md). Dropouts are
kept in the CSV with empty metric columns so the dropout is
visible rather than hidden.

All six pairwise Pearson correlations stay below the
`|r| < 0.7` falsification threshold documented in
[`docs/PBA.md`](docs/PBA.md), now on the extended sample of 247
valid points. The aggregate flag is the worst of the six
pairwise flags so a single overlap is enough to raise it.

The three pairs involving the persistence axis sit inside the
`|r| < 0.7` band on the extended sample as well:
`closure-persistence` at `−0.61`, `memory-persistence` at
`−0.33`, and `constraint-persistence` at `−0.07`. This is the
empirical correlation gate pre-registered in
[`docs/RAI.md`](docs/RAI.md) ("Empirical correlation `|r| < 0.7`
on the benchmark zoo"). Together with the static no-cross-import
audit baked into `compute_rai_proxy_persistence`, it is the
falsification criterion the fourth axis had to clear before
being considered a fourth dimension of the autonomy atlas rather
than a re-skin of an existing axis. The `closure–persistence`
correlation has tightened from `−0.44` (v0.7.0a0) to `−0.61`
(v0.7.2a0) on the larger sample, but still sits below the
falsification threshold; the same `closure–persistence` pair
also flips to `−0.07` *within* `KauffmanNetwork` and to `−1.00`
*within* `SimpleAutomaton`, raising the Simpson's-paradox health
flag analysed in
[`docs/ATLAS_GEOMETRY.md`](docs/ATLAS_GEOMETRY.md).

The third axis cleanly **breaks the closure-saturation wall**
identified in `v0.5.0a0`: single-node periodic cycles and
self-generated `SimpleAutomaton` systems, which previously sat
indistinguishably from ECA rings on the vertical line
`closure = 1.0`, now drop to `constraint = 0.0` while ECA rings
stay at `constraint = 1.0`. The wall is therefore not resolved
(closure still saturates by construction in fully-observed
deterministic systems) but it is no longer the only readable
signal.

A scatter rendering of the same CSV — points placed on the
`(closure, memory)` plane, with marker size proportional to the
`constraint` axis — is shipped at
[`docs/benchmarks/v0.7.2a0.png`](docs/benchmarks/v0.7.2a0.png),
and the captured stdout of the reference run lives at
[`docs/benchmarks/v0.7.2a0.log.txt`](docs/benchmarks/v0.7.2a0.log.txt)
for traceability. The persistence axis is reported in the CSV's
fourth metric column and is rendered separately as a domain-of-
applicability curve under
[`docs/benchmarks/persistence_v0.7.0.png`](docs/benchmarks/persistence_v0.7.0.png).
The two-axis baseline from `v0.5.0a0`
([`csv`](docs/benchmarks/v0.5.0a0.csv) /
[`png`](docs/benchmarks/v0.5.0a0.png)), the three-axis snapshot
from `v0.6.0a0` ([`csv`](docs/benchmarks/v0.6.0a0.csv) /
[`png`](docs/benchmarks/v0.6.0a0.png)), and the four-axis
short-sample snapshot from `v0.7.0a0`
([`csv`](docs/benchmarks/v0.7.0a0.csv) /
[`png`](docs/benchmarks/v0.7.0a0.png)) are kept under
`docs/benchmarks/` for traceability.

### Atlas geometry analysis (`v0.7.2a0`)

`v0.7.2a0` ships a pre-registered geometric audit of the
four-axis cloud, designed *before* any extended-sweep data was
seen. The full pre-registration, threshold table, implementation
report, and verdict live in
[`docs/ATLAS_GEOMETRY.md`](docs/ATLAS_GEOMETRY.md). Headline
indicators on the 247 valid points:

| Indicator                        | Value   | Pre-registered band             |
|----------------------------------|--------:|---------------------------------|
| `λ_1`                            | `0.469` | `[0.40, 0.70)` — inconclusive   |
| `λ_1 + λ_2`                      | `0.809` | `[0.65, 0.85)` — partial low-D  |
| `s(k* = 5)` (silhouette, k-means)| `0.642` | `≥ 0.50` — strong cluster       |
| Adapter-class alignment          |  4 of 5 | clusters dominated by one class |

The combination is not a clean fit to any of the three
pre-registered outcomes (Level 2 reinforced, inconclusive,
Level 3 suspected); per the resolution rule pre-registered in
[`docs/ATLAS_GEOMETRY.md`](docs/ATLAS_GEOMETRY.md), the verdict
is

> **Inconclusive on the level question (PCA reading), with a
> Level-3-suggestive overlay (clustering reading).**

A Simpson's-paradox health flag is also raised: several global
pairwise correlations are partly artefacts of the substrate
composition of the zoo (the most extreme case is
`closure–persistence`, global `−0.61` vs `−1.00` within
`SimpleAutomaton` alone). The level question — Level 2 (one
multidimensional object) vs Level 3 (several objects sharing a
label) — is therefore genuinely *under-determined* on the
structural domain and is pushed to `v0.9.0`'s behavioural
validation against transcript-based RAI for a clean arbitration.

Reproducing the analysis:

```bash
pip install -e ".[dev]"
python examples/atlas_geometry.py        # writes docs/benchmarks/atlas_geometry_v0.7.2a0.json
pip install -e ".[dev,viz]"
python examples/atlas_geometry_plot.py   # writes docs/benchmarks/atlas_geometry_v0.7.2a0.png
```

The biplot
([`docs/benchmarks/atlas_geometry_v0.7.2a0.png`](docs/benchmarks/atlas_geometry_v0.7.2a0.png))
renders the PCA scree (with the pre-registered `λ_1 ≥ 0.70`
reference line) and the PC1/PC2 projection of the standardised
4-D cloud with axis loadings drawn as labelled arrows. t-SNE /
UMAP panels are deliberately omitted; the pre-registration
flagged them as illustrative-only because they can manufacture
visual clusters from isotropic noise.

### Saturation diagnostic (`v0.5.1a0`)

The most visible feature of the scatter above is the vertical wall
of points at `closure = 1.0`. The `v0.5.1a0` diagnostic shows that
this wall is a **theorem about the metric**, not a flaw: any
deterministic system whose observed `(S, E)` pair already covers
every variable the transition rule depends on satisfies
`H(S_{t+1} | S_t, E_t) = 0`, which forces
`I(S_{t+1}; S_t | E_t) = H(S_{t+1} | E_t)`, which forces
`closure = 1.0`. Three of the four adapter classes in the benchmark
(ECA, PeriodicCycle, self-generated `SimpleAutomaton`) satisfy
those preconditions; the fourth (KauffmanNetwork) breaks them on
purpose, which is why it is the only adapter whose closure values
vary continuously across the unit interval.

To verify the theorem empirically, the diagnostic injects
Bernoulli bit-flip noise into the focal trajectory of a saturating
ECA (rule 110) at probabilities `p ∈ {0, 0.01, …, 0.50}` and
re-measures closure. The expected behaviour is a smooth, monotonic
fall off the wall.

```bash
pip install -e ".[dev]"
python examples/saturation_diagnostic.py        # writes docs/benchmarks/saturation_v0.5.1.csv
pip install -e ".[dev,viz]"
python examples/saturation_plot.py              # writes docs/benchmarks/saturation_v0.5.1.png
```

Headline numbers from the snapshot shipped here
(`docs/benchmarks/saturation_v0.5.1.csv`, 10 noise levels × 5 seeds
= 50 valid points):

| Noise probability `p` | closure (mean ± std) | memory (mean ± std) |
|----------------------:|---------------------:|--------------------:|
| 0.00                  | 1.000 ± 0.000        | 0.569 ± 0.033       |
| 0.01                  | 0.810 ± 0.051        | 0.536 ± 0.021       |
| 0.05                  | 0.434 ± 0.055        | 0.405 ± 0.016       |
| 0.10                  | 0.234 ± 0.032        | 0.284 ± 0.045       |
| 0.20                  | 0.059 ± 0.010        | 0.121 ± 0.030       |
| 0.50                  | 0.001 ± 0.001        | 0.070 ± 0.010       |

The full curve is rendered at
[`docs/benchmarks/saturation_v0.5.1.png`](docs/benchmarks/saturation_v0.5.1.png).
Two practical reads:

- The wall at `closure = 1.0` is **fragile**, not robust. A 1 %
  per-step bit-flip rate already drops closure to `0.81`, and
  closure converges to zero by `p ≈ 0.3`.
- A closure value strictly below 1.0 is therefore informative.
  In practice it signals partial observation, stochastic dynamics
  or measurement noise — exactly the three failure modes the
  metric is designed to detect.

The formal statement of the theorem and its consequences for PBA
live in [`docs/PBA.md` § "Domain of applicability"](docs/PBA.md#domain-of-applicability)
(Spanish: [`docs/PBA.es.md`](docs/PBA.es.md)).

### Constraint-closure density diagnostic (`v0.6.1a0`)

The constraint-closure axis introduced in `v0.6.0a0` carries
its own pair of boundary regions, formalised as theorems and
verified with the same diagnostic-grade rigour the closure axis
got in `v0.5.1a0`:

- **Theorem A — single-constraint trivial-zero.** Any system
  with `n = 1` update function returns `constraint = 0.0` by
  construction (a simple cycle of length 2 or 3 requires at
  least two distinct nodes). Covers `PeriodicCycle` and
  `SimpleAutomaton`.
- **Theorem B — symmetric-neighbour saturation.** Any graph in
  which every node reads at least one node that reads it back
  returns `constraint = 1.0` by construction (every node sits
  on a length-2 cycle). Covers `ECASystem` on any non-trivial
  periodic ring.

To verify both theorems jointly, the diagnostic sweeps the
connection density of a controllable system. For each
`K ∈ {1, …, n − 1}` it generates several Kauffman networks of
size `n` and computes `constraint_closure` directly from the
causal graph (no trajectory needed; the metric is purely
topological).

```bash
pip install -e ".[dev]"
python examples/constraint_density_diagnostic.py        # writes docs/benchmarks/constraint_density_v0.6.1.csv
pip install -e ".[dev,viz]"
python examples/constraint_density_plot.py              # writes docs/benchmarks/constraint_density_v0.6.1.png
```

Headline numbers from the snapshot shipped here
(`docs/benchmarks/constraint_density_v0.6.1.csv`, 9 K values × 10
seeds = 90 measurements at `n = 10`):

| Input degree `K` | constraint (mean ± std) |
|-----------------:|------------------------:|
| 1                | 0.140 ± 0.120           |
| 2                | 0.520 ± 0.236           |
| 3                | 0.790 ± 0.138           |
| 4                | 0.950 ± 0.067           |
| 5                | 0.980 ± 0.060           |
| 6                | 1.000 ± 0.000           |
| 7                | 1.000 ± 0.000           |
| 8                | 1.000 ± 0.000           |
| 9                | 1.000 ± 0.000           |

The full curve is rendered at
[`docs/benchmarks/constraint_density_v0.6.1.png`](docs/benchmarks/constraint_density_v0.6.1.png).

Two practical reads:

- The metric is a **monotone sigmoid** in connection density.
  At `K = 1` it sits near Theorem A's lower boundary; at
  `K ≥ 6` (with `n = 10`) every seed identically saturates at
  `1.0` (`std = 0`), reaching Theorem B's upper boundary.
- A constraint-closure value of `0.0` does **not** mean "no
  autonomy". On a single-constraint adapter the metric is
  silent by Theorem A; the system simply sits outside its
  discriminative domain. Symmetrically, `1.0` does not mean
  "fully autonomous" — on a dense periodic ring it is forced
  by Theorem B regardless of dynamical content.

Both theorems and the diagnostic are documented in
[`docs/CONSTRAINT_CLOSURE.md` § "Domain of applicability"](docs/CONSTRAINT_CLOSURE.md#domain-of-applicability-added-in-v061a0)
and reflected in
[`docs/PBA.md` § "Domain of applicability"](docs/PBA.md#domain-of-applicability)
(Spanish: [`docs/PBA.es.md`](docs/PBA.es.md)).

### Persistence-vs-coupling diagnostic (`v0.7.0a0`)

The persistence axis added in `v0.7.0a0` ships with a first
domain-of-applicability run that sweeps the **focal coupling** of
a `KauffmanNetwork`. The naïve expectation was a monotone rise
("low coupling → focal flip propagates → low persistence; high
coupling → focal flip invisible → high persistence"). The
diagnostic *falsified* that expectation and revealed a
**U-shape** with two trivial-absorption boundary regimes flanking
a non-trivial middle.

```bash
pip install -e ".[dev]"
python examples/persistence_diagnostic.py        # writes docs/benchmarks/persistence_v0.7.0.csv
pip install -e ".[dev,viz]"
python examples/persistence_plot.py              # writes docs/benchmarks/persistence_v0.7.0.png
```

Headline numbers from the snapshot shipped here
(`docs/benchmarks/persistence_v0.7.0.csv`, 11 coupling levels × 10
seeds at `n = 10`, `k = 3`):

| Focal coupling | persistence (mean ± std) | n_valid / n_total |
|---------------:|-------------------------:|------------------:|
| 0.00           | 1.000 ± 0.000            | 6 / 10            |
| 0.10           | 1.000 ± 0.000            | 6 / 10            |
| 0.20 – 0.50    | 0.556 ± 0.453            | 8 / 10            |
| 0.60 – 0.80    | 0.415 ± 0.465            | 9 / 10            |
| 0.90           | 0.665 ± 0.406            | 9 / 10            |
| 1.00           | 0.665 ± 0.406            | 9 / 10            |

The full curve is rendered at
[`docs/benchmarks/persistence_v0.7.0.png`](docs/benchmarks/persistence_v0.7.0.png).
Two practical reads:

- **Low-coupling boundary (coupling ≈ 0).** Most seeds drop
  because the focal trajectory collapses to a constant (a 1-bit
  rule generally has a fixed point). The seeds that survive
  score `persistence ≈ 1` not because the system *defends* its
  trajectory, but because the perturbation is absorbed by the
  fixed point in one step. This is **trivial absorption by
  collapse**, not autonomy.
- **High-coupling boundary (coupling ≈ 1).** The focal node
  ignores its own previous value, so the focal flip never enters
  the rule that computes the focal at `t_star + 1`. The metric
  returns `persistence ≈ 1` by construction. This is **trivial
  absorption by invisibility**, again not autonomy.

The non-trivial useful range of the metric on Kauffman networks
sits in the intermediate couplings, where actual perturbation
propagation is observed. The U-shape is the persistence analogue
of the closure-saturation theorem (`v0.5.1a0`) and the
symmetric-neighbour saturation theorem for constraint-closure
(`v0.6.1a0`): the metric has structurally trivial regions at the
edges of its parameter space and a non-trivial useful range in
the middle. Formalising the two boundary theorems for persistence
(jointly with the deferred perturbation-magnitude sweep) is the
planned content of the `v0.7.1` maintenance cycle.

## Adapters

- **`SimpleAutomaton`** — two factory constructors
  (`from_self_generated_rules`, `from_external_rules`) for synthetic
  toy systems.
- **`CSVTrajectory`** — loads a user-supplied two-column CSV with
  discrete integer `state` and `env` columns.
- **LLM transcript** — planned for a later alpha.

Any object implementing `get_state_history()` and `get_env_history()`
(both returning 1D integer `np.ndarray`) satisfies the
`AutonomySystem` protocol and can be passed to `Autonometer.measure`.

## Theoretical grounding

`autonometrics` does not introduce a new theory of autonomy. It
operationalises a recurring *ratio of internal over total* shape
that already runs through several traditions in the structural
self-determination literature. The intended scope and the
falsification criteria for that unifying claim are stated in
[`docs/PBA.md`](docs/PBA.md); the references the current axes
build on are:

- Bertschinger, N., Olbrich, E., Ay, N., & Jost, J. (2008).
  *Autonomy: An Information-Theoretic Perspective*. BioSystems —
  introduces the conditional-information core measured by the
  closure axis.
- Albantakis, L. (2021). *Quantifying the Autonomy of Structurally
  Diverse Automata: A Comparison of Candidate Measures*. Entropy —
  comparative review and the normalisation form used here.
- Crutchfield, J. P., & Young, K. (1989). *Inferring statistical
  complexity*. Physical Review Letters — introduces excess entropy,
  the engine behind the memory axis.
- Feldman, D. P., & Crutchfield, J. P. (2002). *Measures of
  Statistical Complexity: Why?*. Physics Letters A — formal critique
  of LMC-style "balance" measures that drove the migration done in
  `v0.3.0-alpha`.
- Farnsworth, K. D. (2018). *How Organisms Gained Causal Independence
  and How It Might Be Quantified*. Biology — argues that autonomous
  agency requires two jointly necessary features (organisational
  closure and an internalised objective-function providing a 'goal'),
  and proposes Integrated Information Theory as a possible
  quantification. The two-axis shape of the plane here is *inspired
  by* this dual-feature thesis, not a literal implementation of it:
  the memory ratio is a structural proxy for ongoing activity, not
  an objective-function measurement.
- Montévil, M., & Mossio, M. (2015). *Biological organisation as
  closure of constraints*. Journal of Theoretical Biology — formal
  framework where biological organisation is read as mutual
  dependence among constraints (each both produced by and producing
  the others). Reference for the `constraint_closure` axis shipped
  in `v0.6.0a0`; the operational mapping from the paper's
  primitives to the package's discrete-graph implementation is
  documented in
  [`docs/CONSTRAINT_CLOSURE.md`](docs/CONSTRAINT_CLOSURE.md).

## Related work

`autonometrics` overlaps with several adjacent toolkits. The
relevant difference is *framing*, not the underlying mathematics:
none of the tools below collects information-theoretic measures
under a single internal-over-total ratio convention, and most are
either deeper (and substrate-bound) or more general (and unframed).

- [`Albantakis/autonomy`](https://github.com/Albantakis/autonomy) —
  toolbox for comparing autonomy measures on small simulated agents
  represented as transition probability matrices. Authored by the
  same researcher whose 2021 review article this package builds on.
  Requires PyPhi, runs on Linux and macOS only, and outputs a
  multi-column DataFrame intended for cross-measure comparison
  rather than a single normalised reading. `autonometrics` does not
  depend on it: the closure-axis formula is reimplemented in pure
  `numpy` so the package runs on Linux, macOS *and* Windows alike,
  and so it accepts arbitrary discrete trajectories instead of
  pre-built transition probability matrices.
- [JIDT](https://github.com/jlizier/jidt) — Java toolkit for
  information-theoretic measures (transfer entropy, active
  information storage, predictive information / excess entropy,
  mutual information). The numerical engine many adjacent papers
  build on; cross-language but not a unified autonomy index.
- [PyInform](https://github.com/ELIFE-ASU/PyInform) — Python wrapper
  on the Inform C library. Provides `active_info`, `block_entropy`,
  `entropy_rate`, `transfer_entropy` and related building blocks.
- [PyPhi](https://github.com/wmayner/pyphi) — reference IIT
  implementation (Φ, MIP) on transition probability matrices. A
  different formalism from the closure axis used here; a possible
  optional dependency for an IIT-based axis later in the roadmap.
- [dit](https://github.com/dit/dit) — general discrete information
  theory toolkit (PID, divergences, multivariate measures). A
  candidate numerical dependency for future axes that need partial
  information decomposition.

The cross-platform, dependency-light stance is deliberate. The
package targets researchers, students and applied users who want a
working measurement on whatever machine they have, including
Windows. Pure-`numpy` implementations are preferred over
heavier dependencies until a future axis genuinely needs them; if
that ever happens, the heavy dependency will be opt-in via
`extras_require` rather than mandatory.

## Roadmap

Each future alpha adds one more `[0, 1]`-valued ratio drawn from
the structural self-determination literature, keeping the same
PBA convention so all axes remain comparable. The order below
prioritises empirical validation of the existing axes before
broadening them: the first benchmark run shipped in `v0.5.0a0`
established that `closure` and `memory` carry distinct
information on the current adapter zoo, the `v0.5.1a0`
diagnostic mapped the `closure = 1.0` saturation wall,
`v0.6.0a0` added the third axis to break that wall while
preserving pairwise independence, `v0.6.1a0` mapped the two
saturating regions of `constraint_closure`, `v0.7.0a0` added
the fourth axis (`rai_proxy_persistence`) and revealed its U-
shaped domain of applicability, `v0.7.2a0` ran a
pre-registered geometric audit of the four-axis cloud whose
verdict pushed the Level 2 vs Level 3 question to `v0.9.0`,
and `v0.8.0a0` added the fifth axis (`coherence` / Theil's U)
together with its reference adapter `PromisedCycle`, ran the
Session B diagnostic block (independence audit + causal
experiment with `p_env`) that overrode the pre-registered hard
gate on causal grounds, and shipped the **mosaic-atlas
verdict** (`n_valid_full = 0/645`: no system in the current
zoo has all five axes simultaneously, so the atlas is best
read as overlapping four-axis sub-charts rather than a single
five-dimensional cloud).

- `v0.5.0-alpha`: benchmark suite + scatter plot. Reference
  systems (`ECASystem`, `KauffmanNetwork`, `PeriodicCycle`) wired
  into a sweep that measures `(closure, memory)` over multiple
  seeds and reports correlation against the PBA falsification
  threshold.
- `v0.5.1-alpha`: saturation diagnostic. Bernoulli bit-flip
  noise sweep on a saturating ECA, formal statement of the
  closure-saturation theorem, and the "domain of applicability"
  section in `docs/PBA.md`.
- `v0.6.0-alpha`: third axis — `constraint_closure` (Montévil &
  Mossio-style). Per-adapter causal-graph implementations,
  three-axis benchmark snapshot with three pairwise
  correlations, and an independence-by-design audit.
- `v0.6.1-alpha`: domain-of-applicability diagnostic for
  `constraint_closure`. Formal statement of the
  single-constraint trivial-zero theorem and the
  symmetric-neighbour saturation theorem; Kauffman density
  sweep snapshot under
  `docs/benchmarks/constraint_density_v0.6.1.*`.
- `v0.7.0-alpha`: fourth axis — `rai_proxy_persistence` (Lee &
  McShea-style perturbation persistence, RAI-style structural
  proxy). Adapter-side `replay_from_perturbation` protocol,
  four-axis benchmark snapshot with six pairwise correlations
  (all `|r| < 0.7`), and a first persistence-vs-coupling
  diagnostic that revealed the U-shape boundary regimes.
  Pre-registered in [`docs/RAI.md`](docs/RAI.md).
- `v0.7.1-alpha`: domain-of-applicability cycle for
  `rai_proxy_persistence`. Formal statement of the two boundary
  theorems (low-coupling collapse and high-coupling
  invisibility), perturbation-magnitude sweep already deferred
  there in `docs/RAI.md`, and the same diagnostic-grade rigour
  the prior axes already enjoy. Intentionally **skipped** in
  the chronological release order; the boundary theorems and
  the magnitude sweep land here.
- `v0.7.2-alpha`: pre-registered atlas-geometry analysis. PCA
  + k-means + silhouette + conditional correlations on the
  extended four-axis benchmark (`n_valid = 247`).
  Pre-registered in
  [`docs/ATLAS_GEOMETRY.md`](docs/ATLAS_GEOMETRY.md). Verdict:
  inconclusive on the level question (PCA reading), with a
  Level-3-suggestive overlay (clustering reading); the level
  question is pushed to `v0.9.0`'s behavioural validation.
- `v0.8.0-alpha` *(current)*: fifth axis —
  **coherence-based alignment** (`cba_theil_u`, Theil's U on
  declared vs executed trajectories with Miller-Madow bias
  correction). New reference adapter `PromisedCycle` with
  optional independent declared-channel noise (`p_env`); new
  optional protocol method `get_declared_executed`; new
  `AutonomyProfile.cba_theil_u` field. Pre-registered in
  [`docs/CBA.md`](docs/CBA.md). Five-axis benchmark snapshot
  at `docs/benchmarks/v0.8.0a0.{csv,log.txt}`. Session B ships
  three diagnostic snapshots:
  `cba_independence_v0.8.0a0.{json,png,log.txt}` (stratified
  audit, Simpson's-paradox visualisation),
  `cba_env_decouple_v0.8.0a0.{json,png,log.txt}` (causal
  experiment with `p_env`, `r(closure, coherence)` falls from
  `+0.97` to `+0.48` and `r(coherence, p_env) = +0.0007`
  confirms Theil's U invariance), and the
  [v0.8.0a0 follow-up](docs/ATLAS_GEOMETRY.md#v080a0-follow-up--five-axis-geometry-atlas-as-a-mosaic)
  of `ATLAS_GEOMETRY.md` (Step 7 verdict:
  `n_valid_full = 0/645`, atlas is a mosaic of overlapping
  four-axis sub-charts). Pre-registered hard gate
  (`|r| ≥ 0.9`) was triggered by the headline `+0.96` and
  then **overridden on causal grounds** with the override
  documented in the post-mortem section of
  [`docs/CBA.md`](docs/CBA.md). Level question pulled toward
  Level 3, decided (or stays open) at `v0.9.0`.
- `v0.9.0-alpha`: LLM transcript adapter (bring-your-own labels)
  and additional public-dataset benchmarks. **Behavioural
  validation pass**: arbitrates Level 2 vs Level 3 against
  transcript-based RAI, the test the structural geometry
  cannot run alone.
- `v1.0.0` (without alpha marker): PyPI publication once five
  ratios, three adapters, and the full benchmark battery are
  stable.

## License

MIT. See [LICENSE](LICENSE).
