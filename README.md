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

## Roadmap

The v0.1.0a0 milestone implements a single metric (Albantakis-style
conditional mutual information) applied to simple automata. Additional
metrics (Gershenson autopoietic ratio, SDT Relative Autonomy Index,
Coherence-Based Alignment score) and additional adapters (LLMs,
organisations) are planned once the core is validated.

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
