"""End-to-end integration tests: the hello-world claim of the MVP."""

import numpy as np
import pytest

from autonometrics import Autonometer, AutonomyProfile, SimpleAutomaton


@pytest.mark.parametrize("seed", [0, 1, 7, 17, 42])
def test_self_generated_scores_higher_than_external(seed: int) -> None:
    """Across several seeds, a self-ruled automaton is measurably more autonomous."""
    rng = np.random.default_rng(seed)
    env = rng.integers(0, 3, size=3000).astype(np.int64)

    a = SimpleAutomaton.from_self_generated_rules(n_states=4, env=env, seed=seed)
    b = SimpleAutomaton.from_external_rules(n_states=4, env=env, seed=seed)

    meter = Autonometer()
    profile_a = meter.measure(a)
    profile_b = meter.measure(b)

    assert isinstance(profile_a, AutonomyProfile)
    assert isinstance(profile_b, AutonomyProfile)
    assert profile_a.ratio_endo_total > profile_b.ratio_endo_total + 0.3


def test_profile_metadata_is_populated() -> None:
    rng = np.random.default_rng(0)
    env = rng.integers(0, 3, size=1500).astype(np.int64)
    a = SimpleAutomaton.from_self_generated_rules(n_states=4, env=env, seed=0)

    profile = Autonometer().measure(a)

    assert profile.metadata["metric"] == "albantakis"
    assert profile.metadata["adapter"] == "SimpleAutomaton"
    assert profile.metadata["n_timesteps"] == 1500
