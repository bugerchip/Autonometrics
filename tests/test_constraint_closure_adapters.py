"""Adapter-level tests for ``constraint_closure``.

These tests check that each adapter's ``get_causal_graph`` is
consistent with the design predictions in
``docs/CONSTRAINT_CLOSURE.md`` and that the resulting
constraint-closure scores fall in the expected ranges.
"""

from __future__ import annotations

import numpy as np
import pytest

from autonometrics.adapters import SimpleAutomaton
from autonometrics.benchmarks import ECASystem, KauffmanNetwork, PeriodicCycle
from autonometrics.core import Autonometer
from autonometrics.metrics.constraint_closure import compute_constraint_closure


@pytest.mark.parametrize("rule", [30, 90, 110, 184])
def test_eca_graph_is_three_neighbour_periodic(rule: int) -> None:
    """Each ECA cell depends on its left, self, and right neighbour."""
    eca = ECASystem(rule=rule, n_steps=20, width=11, seed=0)
    graph = eca.get_causal_graph()

    assert graph.shape == (11, 11)
    assert graph.dtype == np.bool_

    for p in range(11):
        expected = {(p - 1) % 11, p, (p + 1) % 11}
        actual = {int(j) for j in np.where(graph[p])[0]}
        assert actual == expected


@pytest.mark.parametrize("rule", [30, 90, 110, 184])
def test_eca_constraint_closure_is_one(rule: int) -> None:
    """ECA rings have causal_graph[i, i+/-1] both True, so closure=1.0."""
    eca = ECASystem(rule=rule, n_steps=20, width=11, seed=0)
    graph = eca.get_causal_graph()
    assert compute_constraint_closure(graph) == 1.0


def test_periodic_cycle_constraint_closure_is_zero() -> None:
    """Single-constraint systems cannot satisfy length>=2 closure."""
    pc = PeriodicCycle(period=5, n_steps=40)
    graph = pc.get_causal_graph()

    assert graph.shape == (1, 1)
    assert graph[0, 0]
    assert compute_constraint_closure(graph) == 0.0


def test_simple_automaton_self_generated_constraint_closure_is_zero() -> None:
    env = np.array([0, 1, 2, 0, 1, 2] * 8, dtype=np.int64)
    auto = SimpleAutomaton.from_self_generated_rules(n_states=4, env=env, seed=0)
    graph = auto.get_causal_graph()

    assert graph.shape == (1, 1)
    assert graph[0, 0]
    assert compute_constraint_closure(graph) == 0.0


def test_simple_automaton_external_constraint_closure_is_zero() -> None:
    env = np.array([0, 1, 2, 0, 1, 2] * 8, dtype=np.int64)
    auto = SimpleAutomaton.from_external_rules(n_states=4, env=env, seed=0, noise=0.2)
    graph = auto.get_causal_graph()

    assert graph.shape == (1, 1)
    assert not graph[0, 0]
    assert compute_constraint_closure(graph) == 0.0


def test_kauffman_graph_has_k_inputs_per_node() -> None:
    """Each node's row has at most k True entries (deduplicated)."""
    n_nodes = 8
    k = 3
    network = KauffmanNetwork(n_nodes=n_nodes, k=k, n_steps=30, coupling=1.0, seed=0)
    graph = network.get_causal_graph()

    assert graph.shape == (n_nodes, n_nodes)
    for i in range(n_nodes):
        assert graph[i].sum() <= k


@pytest.mark.parametrize("k", [1, 2, 3])
def test_kauffman_graph_matches_inputs_attribute(k: int) -> None:
    """The exposed graph must agree with the network's internal wiring."""
    n_nodes = 6
    network = KauffmanNetwork(n_nodes=n_nodes, k=k, n_steps=20, coupling=1.0, seed=42)
    graph = network.get_causal_graph()

    inputs = network._inputs
    assert inputs.shape == (n_nodes, k)
    for i in range(n_nodes):
        for src in inputs[i]:
            assert graph[i, int(src)]


def test_kauffman_k1_constraint_closure_is_low_on_average() -> None:
    """K=1 networks rarely form length-2 / length-3 cycles."""
    scores: list[float] = []
    for seed in range(30):
        network = KauffmanNetwork(n_nodes=10, k=1, n_steps=20, coupling=1.0, seed=seed)
        scores.append(compute_constraint_closure(network.get_causal_graph()))
    assert np.mean(scores) < 0.4


def test_kauffman_k3_constraint_closure_is_high_on_average() -> None:
    """K=3 networks frequently form length-2 / length-3 cycles."""
    scores: list[float] = []
    for seed in range(30):
        network = KauffmanNetwork(n_nodes=10, k=3, n_steps=20, coupling=1.0, seed=seed)
        scores.append(compute_constraint_closure(network.get_causal_graph()))
    assert np.mean(scores) > 0.5


def test_autonometer_records_constraint_closure_on_eca() -> None:
    eca = ECASystem(rule=110, n_steps=600, width=21, seed=0)
    profile = Autonometer(metrics=["albantakis", "memory", "constraint_closure"]).measure(eca)
    assert profile.constraint_closure == 1.0
    assert profile.ratio_endo_total is not None
    assert profile.memory_endo_ratio is not None


def test_autonometer_records_constraint_closure_on_periodic_cycle() -> None:
    pc = PeriodicCycle(period=4, n_steps=600)
    profile = Autonometer(metrics=["albantakis", "memory", "constraint_closure"]).measure(pc)
    assert profile.constraint_closure == 0.0


def test_autonometer_returns_none_when_adapter_lacks_graph(tmp_path) -> None:
    """CSVTrajectory does not implement ``get_causal_graph``.

    The orchestrator must record ``None`` for the constraint-closure
    field rather than aborting the whole measurement.
    """
    from autonometrics.adapters import CSVTrajectory

    rng = np.random.default_rng(0)
    csv_path = tmp_path / "traj.csv"
    rows = ["state,env"]
    state = 0
    for _ in range(800):
        env_val = int(rng.integers(0, 3))
        next_state = (state + env_val + int(rng.integers(0, 2))) % 3
        rows.append(f"{state},{env_val}")
        state = next_state
    csv_path.write_text("\n".join(rows), encoding="utf-8")

    traj = CSVTrajectory.from_path(csv_path)
    profile = Autonometer(metrics=["albantakis", "memory", "constraint_closure"]).measure(traj)
    assert profile.constraint_closure is None
    assert profile.ratio_endo_total is not None
    assert profile.memory_endo_ratio is not None
