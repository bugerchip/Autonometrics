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
self-determination can be read as a *ratio of internal magnitude over
total magnitude*. Several traditions in the autonomy literature share
that common shape, and `autonometrics` collects them under it so
points from different substrates land in the same comparable space.
PBA is treated as a falsifiable working hypothesis, not as an axiom
— see [`docs/PBA.md`](docs/PBA.md) for the full statement and
falsification criteria (Spanish version: [`docs/PBA.es.md`](docs/PBA.es.md)).

## Installation

This package is not yet published to PyPI. Install from source in
development mode:

```bash
git clone https://github.com/bugerchip/Autonometrics.git
cd Autonometrics
pip install -e ".[dev]"
```

Requires Python 3.10 or later.

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

Two metrics ship in the current alpha. Both follow the PBA *internal
over total* shape, both live in `[0.0, 1.0]`, and both are exposed as
pure `numpy` functions wired into `Autonometer`:

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

Both scores are returned in a single `AutonomyProfile` with
`Optional[float]` fields, so unrequested metrics stay `None`.

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
  the others). Reference for the constraint-closure axis planned
  in the roadmap.

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
PBA convention so all axes remain comparable.

- `v0.5.0-alpha`: third axis — RAI-style relative autonomy ratio
  (Deci & Ryan).
- `v0.6.0-alpha`: fourth axis — coherence-based alignment ratio.
- `v0.7.0-alpha`: fifth axis — constraint-closure ratio
  (Montévil & Mossio-style).
- `v0.8.0-alpha`: LLM transcript adapter (bring-your-own labels).
- `v0.9.0-alpha`: benchmarks against public datasets (boolean
  networks, elementary cellular automata).
- `v0.1.0` (without alpha marker): PyPI publication once five ratios,
  three adapters, and baseline benchmarks are stable.

## License

MIT. See [LICENSE](LICENSE).
