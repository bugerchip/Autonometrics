# autonometrics

> An instrument for quantifying structural self-determination across systems.

**Status:** `alpha` — work in progress, API unstable.

`autonometrics` is a Python package that applies existing formalisations of
autonomy and self-determination to any agentic system (automata, AI agents,
humans via survey data, organisations) and returns comparable, normalised
measurements. It is a measurement tool, not a new theory: it packages
established measures from information theory and dynamical-systems
analysis behind a single, cross-substrate API.

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

print(profile_a.ratio_endo_total, profile_a.structural_memory)
print(profile_b.ratio_endo_total, profile_b.structural_memory)
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

Two metrics ship in the current alpha. Both are exposed as pure `numpy`
functions and wired into `Autonometer`:

### `ratio_endo_total` — Albantakis / Bertschinger closure

Normalised conditional mutual information:

$$A \;=\; \frac{I(S_{t+1};\,S_t \mid E_t)}{H(S_{t+1} \mid E_t)}$$

- `A = 0`: the next state, given the environment, is independent of
  the system's own previous state (no closure, pure drift).
- `A = 1`: the next state, given the environment, is fully determined
  by the system's own previous state (closed dynamics).

### `structural_memory` — Crutchfield excess entropy

Bits of past relevant to future, via block-entropy saturation:

$$E \;=\; H(L) - L \cdot h_\mu, \qquad h_\mu = H(L) - H(L-1)$$

where `H(L)` is the empirical entropy of length-`L` blocks and `L` is
capped by a Grassberger-style rule so every possible block gets about
ten samples on average.

- `E ≈ 0` for a constant sequence *and* for i.i.d. noise — both have
  no useful memory, only different entropy rates.
- `E ≈ log2(p)` for a deterministic period-`p` cycle.
- `E` grows with non-trivial temporal structure.

This replaces the LMC-based `autopoietic_ratio` shipped in `v0.2.x`,
which Feldman & Crutchfield (2002) showed collapses to zero on exactly
the ordered systems that motivated it.

Both scores are returned in a single `AutonomyProfile` with
`Optional[float]` fields, so unrequested metrics stay `None`.

## The autonomy plane

Thinking of the two metrics together, rather than reducing autonomy to
a single number, gives a richer picture. Farnsworth (2018) argues that
genuine autonomy requires at least two independent features: some form
of organisational closure *and* some form of memory-bearing structure.
Our plane puts one on each axis.

| memory ↓ / closure → | **low closure**                 | **high closure**                |
|----------------------|---------------------------------|---------------------------------|
| **low memory**       | drift (noise-driven)            | clockwork regularity            |
| **high memory**      | turbulence / chaos              | candidate autopoietic region    |

- **Drift** (low closure, low memory): the system tracks the
  environment and keeps nothing.
- **Clockwork** (high closure, low memory): determined by its own
  past, but with a trivial repetitive trajectory.
- **Turbulence** (low closure, high memory): the environment shapes
  the system, and the result is long-range but non-self-generated
  structure.
- **Autopoietic region** (high closure, high memory): closed dynamics
  *and* non-trivial trajectory structure — the empirically interesting
  corner of the plane for candidate living and agent-like systems.

The package does not claim to *prove* autopoiesis. It gives a
two-coordinate reading and lets the interpreter argue.

## Adapters

- **`SimpleAutomaton`** — two factory constructors
  (`from_self_generated_rules`, `from_external_rules`) for synthetic
  toy systems.
- **`CSVTrajectory`** — loads a user-supplied two-column CSV with
  discrete integer `state` and `env` columns.
- **LLM transcript** — planned for `v0.4.0-alpha`.

Any object implementing `get_state_history()` and `get_env_history()`
(both returning 1D integer `np.ndarray`) satisfies the
`AutonomySystem` protocol and can be passed to `Autonometer.measure`.

## Theoretical grounding

- Farnsworth, K. D. (2018). *How Organisms Gained Causal Independence
  and How It Might Be Quantified*. Biology — motivates the
  two-feature (closure + memory) view of autonomy.
- Crutchfield, J. P., & Young, K. (1989). *Inferring statistical
  complexity*. Physical Review Letters — introduces excess entropy
  and statistical complexity.
- Feldman, D. P., & Crutchfield, J. P. (2002). *Measures of
  Statistical Complexity: Why?*. Physics Letters A — the formal
  critique of LMC-style "balance" measures that drove the migration
  done in `v0.3.0-alpha`.
- Langton, C. G. (1990). *Computation at the edge of chaos*. Physica
  D — the classic observation that interesting computation sits in a
  narrow band between order and disorder, which the plane above is a
  discrete stand-in for.

## Roadmap

- `v0.4.0-alpha`: LLM transcript adapter (bring-your-own labels).
- `v0.5.0-alpha`: benchmarks against public datasets (boolean
  networks, elementary cellular automata).
- `v0.1.0` (without alpha marker): PyPI publication once two adapters,
  two metrics, and baseline benchmarks are stable.

## References

- Bertschinger, N., Olbrich, E., Ay, N., & Jost, J. (2008).
  *Autonomy: An Information-Theoretic Perspective*. BioSystems.
- Albantakis, L. (2021). *Quantifying the Autonomy of Structurally
  Diverse Automata: A Comparison of Candidate Measures*. Entropy.
- Crutchfield, J. P., & Packard, N. H. (1983). *Symbolic dynamics of
  noisy chaos*. Physica D.
- Crutchfield, J. P., & Young, K. (1989). *Inferring statistical
  complexity*. Physical Review Letters.
- Feldman, D. P., & Crutchfield, J. P. (2002). *Measures of
  Statistical Complexity: Why?*. Physics Letters A.
- Farnsworth, K. D. (2018). *How Organisms Gained Causal Independence
  and How It Might Be Quantified*. Biology.
- Grassberger, P. (1988). *Finite sample corrections to entropy and
  dimension estimates*. Physics Letters A.
- Langton, C. G. (1990). *Computation at the edge of chaos*. Physica D.

## License

MIT. See [LICENSE](LICENSE).
