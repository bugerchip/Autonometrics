"""Canonical-graph tests for ``compute_constraint_closure``.

These tests pin the metric's behaviour on small graphs whose
constraint-closure score can be computed by hand. They are the
specification of the metric.
"""

from __future__ import annotations

import numpy as np
import pytest

from autonometrics.metrics.constraint_closure import compute_constraint_closure


def test_single_node_with_self_loop_scores_zero() -> None:
    """A 1x1 graph with a self-loop has no length-2 / length-3 cycles."""
    graph = np.array([[True]], dtype=bool)
    assert compute_constraint_closure(graph) == 0.0


def test_single_node_without_self_loop_scores_zero() -> None:
    graph = np.array([[False]], dtype=bool)
    assert compute_constraint_closure(graph) == 0.0


def test_two_node_mutual_dependency_scores_one() -> None:
    """Two constraints that depend on each other are fully closed."""
    graph = np.array(
        [
            [False, True],
            [True, False],
        ],
        dtype=bool,
    )
    assert compute_constraint_closure(graph) == 1.0


def test_two_node_one_way_chain_scores_zero() -> None:
    """A pure feed-forward pair has no closure."""
    graph = np.array(
        [
            [False, True],
            [False, False],
        ],
        dtype=bool,
    )
    assert compute_constraint_closure(graph) == 0.0


def test_three_node_triangle_scores_one() -> None:
    """A directed triangle 0->1->2->0 closes all three nodes."""
    graph = np.array(
        [
            [False, True, False],
            [False, False, True],
            [True, False, False],
        ],
        dtype=bool,
    )
    assert compute_constraint_closure(graph) == 1.0


def test_three_node_chain_scores_zero() -> None:
    """A pure linear chain has no length-2 / length-3 cycle."""
    graph = np.array(
        [
            [False, True, False],
            [False, False, True],
            [False, False, False],
        ],
        dtype=bool,
    )
    assert compute_constraint_closure(graph) == 0.0


def test_self_loops_do_not_count_as_closure() -> None:
    """A graph that is *only* self-loops scores 0.0."""
    graph = np.eye(5, dtype=bool)
    assert compute_constraint_closure(graph) == 0.0


def test_long_cycle_alone_scores_zero() -> None:
    """A pure length-4 cycle has no length-2 or length-3 sub-cycles, so 0.0.

    This is the design constraint of the metric: only short
    (mutual or triangular) closures are awarded. A four-clock
    that closes only after four steps is not "mutually
    sustaining" in the local sense Montévil & Mossio target.
    """
    graph = np.array(
        [
            [False, True, False, False],
            [False, False, True, False],
            [False, False, False, True],
            [True, False, False, False],
        ],
        dtype=bool,
    )
    assert compute_constraint_closure(graph) == 0.0


def test_partial_closure_scores_correct_fraction() -> None:
    """Mixed graph: two nodes in a length-2 cycle, two isolated."""
    graph = np.array(
        [
            [False, True, False, False],
            [True, False, False, False],
            [False, False, False, True],
            [False, False, False, False],
        ],
        dtype=bool,
    )
    assert compute_constraint_closure(graph) == pytest.approx(0.5)


def test_complete_directed_graph_scores_one() -> None:
    n = 4
    graph = np.ones((n, n), dtype=bool)
    np.fill_diagonal(graph, False)
    assert compute_constraint_closure(graph) == 1.0


def test_rejects_non_square_matrix() -> None:
    with pytest.raises(ValueError):
        compute_constraint_closure(np.zeros((3, 4), dtype=bool))


def test_rejects_non_2d_input() -> None:
    with pytest.raises(ValueError):
        compute_constraint_closure(np.zeros((3,), dtype=bool))


def test_rejects_empty_graph() -> None:
    with pytest.raises(ValueError):
        compute_constraint_closure(np.zeros((0, 0), dtype=bool))


def test_accepts_integer_input() -> None:
    """Inputs are coerced to boolean; integer adjacency matrices work."""
    graph = np.array([[0, 1], [1, 0]], dtype=np.int64)
    assert compute_constraint_closure(graph) == 1.0


def test_does_not_depend_on_information_theory_imports() -> None:
    """Static audit: the constraint-closure module imports only numpy.

    The PBA design demands that the third axis remain
    independent of the information-theoretic axes
    (``albantakis``, ``memory_ratio``) so that any empirical
    correlation between them is structural rather than
    algebraic. This test asserts that property by reading the
    module's source and verifying the import block.
    """
    import importlib.util
    from pathlib import Path

    module_path = Path(importlib.util.find_spec("autonometrics.metrics.constraint_closure").origin)
    source = module_path.read_text(encoding="utf-8")

    forbidden = [
        "from autonometrics.metrics._entropy",
        "import autonometrics.metrics._entropy",
        "from autonometrics.metrics.albantakis",
        "import autonometrics.metrics.albantakis",
        "from autonometrics.metrics.memory_ratio",
        "import autonometrics.metrics.memory_ratio",
    ]
    for needle in forbidden:
        assert needle not in source, (
            f"constraint_closure must not import {needle!r}; "
            "see docs/CONSTRAINT_CLOSURE.md for the rationale."
        )
