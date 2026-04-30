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

Compare a self-ruled automaton against an externally-driven one:

```python
import numpy as np
from autonometrics import Autonometer, SimpleAutomaton

rng = np.random.default_rng(0)
env = rng.integers(0, 3, size=3000).astype(np.int64)

system_a = SimpleAutomaton.from_self_generated_rules(n_states=4, env=env, seed=0)
system_b = SimpleAutomaton.from_external_rules(n_states=4, env=env, seed=0)

meter = Autonometer()
print(meter.measure(system_a).ratio_endo_total)  # ~1.00
print(meter.measure(system_b).ratio_endo_total)  # ~0.01
```

Or run the bundled demo end-to-end:

```bash
python examples/automaton_demo.py
```

Expected output:

```
Autonometrics v0.1.0a0  Demo

System A (self-generated rules):
  ratio_endo_total: 1.00

System B (externally imposed rules):
  ratio_endo_total: 0.01

Delta = +0.99 (A is more structurally self-determined)
```

## What it measures

The `v0.1.0a0` release implements a single metric, an Albantakis-style
normalised conditional mutual information:

$$A \;=\; \frac{I(S_{t+1};\,S_t \mid E_t)}{H(S_{t+1} \mid E_t)}$$

- `A = 0`: the next state, given the environment, is independent of
  the system's own previous state — the system is fully heteronomous.
- `A = 1`: the next state, given the environment, is fully determined
  by the system's own previous state — the system runs on its own rules.

## Roadmap

Additional metrics (Gershenson autopoietic ratio, SDT Relative Autonomy
Index, Coherence-Based Alignment score) and adapters (LLM transcripts,
human survey data, organisational traces) are planned once the core is
validated. The goal is a multidimensional `AutonomyProfile` vector, not
a single scalar.

## References

The core ideas draw on:

- Bertschinger, N., Olbrich, E., Ay, N., & Jost, J. (2008).
  *Autonomy: An Information-Theoretic Perspective*. BioSystems.
- Albantakis, L. (2021). *Quantifying the Autonomy of Structurally
  Diverse Automata: A Comparison of Candidate Measures*. Entropy.
- Deci, E. L., & Ryan, R. M. (2000). *The "what" and "why" of goal
  pursuits: Human needs and the self-determination of behavior*.
  Psychological Inquiry.

## License

MIT. See [LICENSE](LICENSE).
