"""Hello-world demo: compare a self-ruled automaton with an externally driven one.

Run from the repository root::

    python examples/automaton_demo.py

Both automata observe the same environment trace. System A derives its
transitions from its own previous state; System B derives them from the
environment input. The Albantakis-style conditional mutual information
score should be substantially higher for A than for B.
"""

from __future__ import annotations

import numpy as np

from autonometrics import Autonometer, SimpleAutomaton, __version__


def main() -> None:
    n_states = 4
    n_env_symbols = 3
    n_steps = 3000
    seed = 0

    rng = np.random.default_rng(seed)
    env = rng.integers(0, n_env_symbols, size=n_steps).astype(np.int64)

    system_a = SimpleAutomaton.from_self_generated_rules(n_states=n_states, env=env, seed=seed)
    system_b = SimpleAutomaton.from_external_rules(n_states=n_states, env=env, seed=seed)

    meter = Autonometer()
    profile_a = meter.measure(system_a)
    profile_b = meter.measure(system_b)

    print(f"Autonometrics v{__version__}  Demo")
    print()
    print("System A (self-generated rules):")
    print(f"  ratio_endo_total: {profile_a.ratio_endo_total:.2f}")
    print()
    print("System B (externally imposed rules):")
    print(f"  ratio_endo_total: {profile_b.ratio_endo_total:.2f}")
    print()
    delta = profile_a.ratio_endo_total - profile_b.ratio_endo_total
    print(f"Delta = {delta:+.2f} (A is more structurally self-determined)")


if __name__ == "__main__":
    main()
