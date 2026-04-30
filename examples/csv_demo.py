"""Demo: measure an externally-supplied CSV trajectory.

The script writes a temporary CSV with a self-ruled automaton run and
then loads it through :class:`CSVTrajectory` to show that the same
measurement pipeline works on any user-provided log.

Run from the repository root::

    python examples/csv_demo.py
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np

from autonometrics import Autonometer, CSVTrajectory, SimpleAutomaton, __version__


def main() -> None:
    rng = np.random.default_rng(0)
    env = rng.integers(0, 3, size=3000).astype(np.int64)

    automaton = SimpleAutomaton.from_self_generated_rules(n_states=4, env=env, seed=0)
    state_history = automaton.get_state_history()
    env_history = automaton.get_env_history()

    with tempfile.TemporaryDirectory() as tmp:
        csv_path = Path(tmp) / "trajectory.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as fh:
            fh.write("state,env\n")
            for s, e in zip(state_history, env_history, strict=True):
                fh.write(f"{int(s)},{int(e)}\n")

        trajectory = CSVTrajectory.from_path(csv_path)

        meter = Autonometer(metrics=["albantakis", "autopoietic"])
        profile = meter.measure(trajectory)

    print(f"Autonometrics v{__version__}  CSV demo")
    print()
    print(f"Loaded trajectory: {profile.metadata['n_timesteps']} rows")
    print(f"Adapter: {profile.metadata['adapter']}")
    print(f"Metrics: {profile.metadata['metrics']}")
    print()
    print(f"  ratio_endo_total : {profile.ratio_endo_total:.3f}")
    print(f"  autopoietic_ratio: {profile.autopoietic_ratio:.3f}")


if __name__ == "__main__":
    main()
