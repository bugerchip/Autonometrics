# autonometrics

> An instrument for quantifying structural self-determination across systems.

**Status:** `alpha` — work in progress, API unstable.

`autonometrics` is a Python package that applies existing measures of
autonomy and self-determination to discrete trajectories from
automata, agent traces, simulations and similar systems, returning
comparable normalised scores. It is a measurement tool, not a new
theory: it packages established measures from information theory and
dynamical-systems analysis behind a single, cross-substrate API.

The unifying argument the package follows is the **Principio de
Bordes Autodeterminados (PBA)**: a system's structural
self-determination is a multidimensional phenomenon, and several
traditions in the autonomy literature each operationalise one of
its coordinates as a *ratio of internal magnitude over total
magnitude*. `autonometrics` collects those ratios under a shared
`[0, 1]` normalisation so points from different substrates land
in the same comparable space. The package therefore behaves as
an **atlas of autonomy** — a small set of charts (metrics) that
cover the same territory from different operational angles —
not as a reduction of autonomy to a single underlying quantity.
PBA is treated as a falsifiable working hypothesis at that
multidimensional level, not as an axiom and not as an
entropy-style extensional identity. See
[`docs/PBA.md`](docs/PBA.md) for the full statement, the
three-level taxonomy of unification, and the falsification
criteria (Spanish version: [`docs/PBA.es.md`](docs/PBA.es.md)).

## Installation

This package is not yet published to PyPI. Install from source in
development mode:

```bash
git clone https://github.com/bugerchip/Autonometrics.git
cd Autonometrics
pip install -e ".[dev]"
```

Requires Python 3.10 or later. The core package depends only on
`numpy`. The optional `viz` extra (`pip install -e ".[dev,viz]"`)
adds `matplotlib`, used by the optional benchmark plotting script.

## Quickstart

### Measuring a synthetic automaton

```python
import numpy as np
from autonometrics import Autonometer, SimpleAutomaton

rng = np.random.default_rng(0)
env = rng.integers(0, 3, size=3000).astype(np.int64)

system_a = SimpleAutomaton.from_self_generated_rules(n_states=4, env=env, seed=0)
system_b = SimpleAutomaton.from_external_rules(n_states=4, env=env, seed=0)

meter = Autonometer(metrics=["albantakis", "memory"])
profile_a = meter.measure(system_a)
profile_b = meter.measure(system_b)

print(profile_a.ratio_endo_total, profile_a.memory_endo_ratio)
print(profile_b.ratio_endo_total, profile_b.memory_endo_ratio)
```

### Measuring a CSV trajectory you already have

```python
from autonometrics import Autonometer, CSVTrajectory

trajectory = CSVTrajectory.from_path("my_log.csv")  # header: state,env
profile = Autonometer(metrics=["albantakis", "memory"]).measure(trajectory)
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
`v0.6.0a0` extends it to the third axis (`constraint_closure`)
without changing the system zoo, so the new readings are
directly comparable with the v0.5 baseline. The intent is not to
score one system as "more autonomous" than another. It is to
check whether the three axes carry distinct information for the
systems we can generate today, before adding a fourth axis to
PBA.

Reproducing the run:

```bash
pip install -e ".[dev]"
python examples/benchmark_demo.py        # writes docs/benchmarks/v0.6.0a0.csv
pip install -e ".[dev,viz]"
python examples/benchmark_plot.py        # writes docs/benchmarks/v0.6.0a0.png
```

Headline numbers from the snapshot shipped here
(`docs/benchmarks/v0.6.0a0.csv`):

| Quantity                          | Value     |
|-----------------------------------|-----------|
| Configurations swept              | 69        |
| Fully-valid points                | 48        |
| Configurations dropped (n/a)      | 21        |
| Pearson r(closure, memory)        | +0.32     |
| Pearson r(closure, constraint)    | -0.04     |
| Pearson r(memory, constraint)     | -0.57     |
| Spearman r(closure, memory)       | +0.56     |
| Spearman r(closure, constraint)   | -0.27     |
| Spearman r(memory, constraint)    | -0.45     |
| Falsification threshold           | `|r| < 0.7` |
| Aggregate diagnosis               | OK        |

The 21 dropped configurations correspond to systems whose focal
trajectory collapses to a constant or to a value fully determined
by the environment, in which case `H(S_{t+1} | E_t) = 0` and the
closure ratio is undefined by construction. They are kept in the
CSV with empty metric columns so the dropout is visible rather
than hidden.

All three pairwise Pearson correlations stay below the
`|r| < 0.7` falsification threshold documented in
[`docs/PBA.md`](docs/PBA.md), so on this zoo of systems the three
axes carry distinct information and PBA's *"add more ratios in
the same shape"* roadmap remains motivated. The aggregate flag is
the worst of the three pairwise flags so a single overlap is
enough to raise it.

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
[`docs/benchmarks/v0.6.0a0.png`](docs/benchmarks/v0.6.0a0.png),
and the captured stdout of the reference run lives at
[`docs/benchmarks/v0.6.0a0.log.txt`](docs/benchmarks/v0.6.0a0.log.txt)
for traceability. The two-axis baseline from `v0.5.0a0` is kept
under
[`docs/benchmarks/v0.5.0a0.csv`](docs/benchmarks/v0.5.0a0.csv)
and
[`docs/benchmarks/v0.5.0a0.png`](docs/benchmarks/v0.5.0a0.png).

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
diagnostic mapped the `closure = 1.0` saturation wall, and
`v0.6.0a0` adds the third axis to break that wall while
preserving pairwise independence.

- `v0.5.0-alpha`: benchmark suite + scatter plot. Reference
  systems (`ECASystem`, `KauffmanNetwork`, `PeriodicCycle`) wired
  into a sweep that measures `(closure, memory)` over multiple
  seeds and reports correlation against the PBA falsification
  threshold.
- `v0.5.1-alpha`: saturation diagnostic. Bernoulli bit-flip
  noise sweep on a saturating ECA, formal statement of the
  closure-saturation theorem, and the "domain of applicability"
  section in `docs/PBA.md`.
- `v0.6.0-alpha` *(current)*: third axis —
  `constraint_closure` (Montévil & Mossio-style). Per-adapter
  causal-graph implementations, three-axis benchmark snapshot
  with three pairwise correlations, and an
  independence-by-design audit.
- `v0.7.0-alpha`: fourth axis — RAI-style relative autonomy
  ratio (Deci & Ryan).
- `v0.8.0-alpha`: fifth axis — coherence-based alignment ratio.
- `v0.9.0-alpha`: LLM transcript adapter (bring-your-own labels)
  and additional public-dataset benchmarks.
- `v1.0.0` (without alpha marker): PyPI publication once five
  ratios, three adapters, and the full benchmark battery are
  stable.

## License

MIT. See [LICENSE](LICENSE).
