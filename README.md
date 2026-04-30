# autonometrics

> An instrument for quantifying structural self-determination across systems.

**Status:** `alpha` — work in progress, API unstable.

`autonometrics` is a Python package that applies existing formalisations of
autonomy and self-determination to any agentic system (automata, AI agents,
humans via survey data, organisations) and returns comparable, normalised
measurements. It is a measurement tool, not a new theory: it packages
established measures from information theory, self-determination theory,
and AI safety research behind a single, cross-substrate API.

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

meter = Autonometer(metrics=["albantakis", "autopoietic"])
profile_a = meter.measure(system_a)
profile_b = meter.measure(system_b)

print(profile_a.ratio_endo_total, profile_a.autopoietic_ratio)
print(profile_b.ratio_endo_total, profile_b.autopoietic_ratio)
```

### Measuring a CSV trajectory you already have

```python
from autonometrics import Autonometer, CSVTrajectory

trajectory = CSVTrajectory.from_path("my_log.csv")  # header: state,env
profile = Autonometer(metrics=["albantakis", "autopoietic"]).measure(trajectory)
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
python examples/automaton_demo.py   # self-generated vs externally-driven automata
python examples/csv_demo.py         # round-trip through a CSV file
```

## Metrics

Two metrics ship in v0.2.0-alpha. Both are exposed as pure `numpy`
functions and wired into `Autonometer`:

### `ratio_endo_total` — Albantakis / Bertschinger

Normalised conditional mutual information:

$$A \;=\; \frac{I(S_{t+1};\,S_t \mid E_t)}{H(S_{t+1} \mid E_t)}$$

- `A = 0`: the next state, given the environment, is independent of
  the system's own previous state.
- `A = 1`: the next state, given the environment, is fully determined
  by the system's own previous state.

### `autopoietic_ratio` — Fernandez / Gershenson

Complexity ratio:

$$A \;=\; \frac{C(\text{states})}{C(\text{env})}, \qquad C(x) = 4\,E(x)\,(1 - E(x))$$

where `E(x)` is the normalised Shannon entropy. `C(x)` peaks at
`E = 0.5` (a *balance* between order and disorder), so an i.i.d. uniform
sequence has low complexity, and so does a constant one. Natural range
is `[0, +inf)`:

- `A < 1`: the environment is more complex than the system.
- `A ≈ 1`: system and environment are similarly complex.
- `A > 1`: the system is more complex than the environment
  (autopoietic regime).

Both scores are returned in a single `AutonomyProfile` with
`Optional[float]` fields, so unrequested metrics stay `None`.

## Adapters

- **`SimpleAutomaton`** — two factory constructors (`from_self_generated_rules`,
  `from_external_rules`) for synthetic toy systems.
- **`CSVTrajectory`** — loads a user-supplied two-column CSV with
  discrete integer `state` and `env` columns.
- **LLM transcript** — planned for v0.3.0-alpha.

Any object implementing `get_state_history()` and `get_env_history()`
(both returning 1D integer `np.ndarray`) satisfies the
`AutonomySystem` protocol and can be passed to `Autonometer.measure`.

## Roadmap

- `v0.3.0-alpha`: LLM transcript adapter (bring-your-own labels).
- `v0.4.0-alpha`: benchmarks against public datasets (boolean networks,
  elementary cellular automata).
- `v0.1.0` (without alpha marker): PyPI publication once two adapters,
  two metrics, and baseline benchmarks are stable.

## References

- Bertschinger, N., Olbrich, E., Ay, N., & Jost, J. (2008).
  *Autonomy: An Information-Theoretic Perspective*. BioSystems.
- Albantakis, L. (2021). *Quantifying the Autonomy of Structurally
  Diverse Automata: A Comparison of Candidate Measures*. Entropy.
- Fernandez, N., Maldonado, C., & Gershenson, C. (2014).
  *Information Measures of Complexity, Emergence, Self-organization,
  Homeostasis, and Autopoiesis*. In: Guided Self-Organization:
  Inception, Springer.
- Gershenson, C., & Fernandez, N. (2012). *Complexity and information:
  Measuring emergence, self-organization, and homeostasis at multiple
  scales*. Complexity.
- Deci, E. L., & Ryan, R. M. (2000). *The "what" and "why" of goal
  pursuits: Human needs and the self-determination of behavior*.
  Psychological Inquiry.

## License

MIT. See [LICENSE](LICENSE).
