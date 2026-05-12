"""Montévil-Mossio-style constraint-closure measure of autonomy.

This module operationalises the third PBA axis: the fraction of a
system's structural constraints that participate in **short
mutually-sustaining cycles** of the system's own dependency graph.

The conceptual reference is Montévil & Mossio (2015),
*"Biological organisation as closure of constraints"*
(J. Theor. Biol. 372, 179–191), which separates three primitives:

- **Process**: an event of energy transfer or state transition.
- **Law**: a universal rule governing processes.
- **Constraint**: a material condition that channels processes
  without being consumed by them, with a characteristic time
  scale longer than the processes it channels.

A constraint that is itself produced and maintained by other
constraints of the same system, in such a way that the
dependency graph closes on itself, is said to be under
*organisational closure*. The canonical example is the
membrane ↔ metabolism coupling in a biological cell: each
constraint is sustained by the other.

Operationalisation choices for this implementation are spelled
out in :doc:`docs/CONSTRAINT_CLOSURE` (and revised in the
"Pre-implementation review" section of the same document).
The headline rules:

1. A *constraint* is one update function of the discrete system
   (one per node in a Boolean network, one per cell in a
   cellular automaton, one per cycle rule in a periodic system).
2. Dependency between constraints is **structural** (topology
   of the causal graph); ``causal_graph[i, j] = True`` means
   "the update function of constraint ``i`` reads the state
   controlled by constraint ``j``".
3. A constraint is counted as *closed* when it lies on at least
   one **simple directed cycle of length 2 or 3** in the
   dependency graph. Self-loops (length-1 cycles) are not
   counted: they capture trivial self-reference rather than the
   *network* of distinct constraints Montévil & Mossio require.
   The length-3 ceiling restricts the count to *local* cycles
   so that systems on globally-cyclic boundary conditions (e.g.
   periodic cellular-automaton rings) are not awarded a free
   pass on closure they did not earn organisationally.
4. The metric is the count of such constraints divided by the
   total number of constraints in the system.

Independence-by-design
----------------------
This module is **deliberately information-theory-free**. It
imports only ``numpy`` and works exclusively from the topology
of the causal graph. In particular, it does **not** import any
of:

- ``autonometrics.metrics._entropy``
- ``autonometrics.metrics.albantakis``
- ``autonometrics.metrics.memory_ratio``
- third-party information-theory toolkits (``pyinform``,
  ``dit``, etc.).

This guarantees that any empirical correlation found between
the constraint-closure axis and the two information-theoretic
axes already shipped (Albantakis closure, Crutchfield memory)
is structural, not algebraic. The PBA document
(:doc:`docs/PBA`) makes that independence-by-design a hard
requirement before any cross-axis correlation can count as
evidence for or against the unifying claim.

References
----------
- Montévil, M., & Mossio, M. (2015). *Biological organisation
  as closure of constraints*. Journal of Theoretical Biology
  372, 179–191.
- Mossio, M., Saborido, C., & Moreno, A. (2009). *An
  organizational account of biological functions*. British
  Journal for the Philosophy of Science 60(4), 813–841.
"""

from __future__ import annotations

import numpy as np


def compute_constraint_closure(causal_graph: np.ndarray) -> float:
    """Compute the constraint-closure score of a system.

    Parameters
    ----------
    causal_graph:
        A square 2D array of shape ``(n, n)`` where
        ``causal_graph[i, j]`` is truthy iff "constraint ``i``
        depends on constraint ``j``", i.e. the update function
        of ``i`` reads the state controlled by ``j``. Inputs are
        coerced to boolean. The diagonal encodes self-dependency
        (self-loops); off-diagonal entries encode dependency on
        a distinct constraint.

    Returns
    -------
    float
        A value in ``[0.0, 1.0]``. The fraction of constraints
        that lie on at least one simple directed cycle of length
        2 or 3 in the dependency graph. Self-loops do not count.

    Raises
    ------
    ValueError
        If ``causal_graph`` is not a square 2D array, or if
        ``n == 0``.

    Notes
    -----
    The implementation enumerates length-2 and length-3 cycles
    explicitly. Cost is :math:`O(n^3)` in the worst case, which
    is fine for the discrete adapters shipped with the package
    (``n`` rarely exceeds a few hundred). For very large graphs
    the loop body could be vectorised; we keep the explicit form
    here for readability and auditability.
    """
    matrix = np.asarray(causal_graph, dtype=bool)
    if matrix.ndim != 2:
        raise ValueError(f"causal_graph must be a 2D array, got shape {matrix.shape}")
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"causal_graph must be square, got shape {matrix.shape}")

    n = matrix.shape[0]
    if n == 0:
        raise ValueError("causal_graph must have at least one constraint")

    if n == 1:
        return 0.0

    closed = np.zeros(n, dtype=bool)

    mutual = matrix & matrix.T
    np.fill_diagonal(mutual, False)
    closed |= mutual.any(axis=1)

    if not closed.all():
        for i in range(n):
            if closed[i]:
                continue
            row_i = matrix[i]
            col_i = matrix[:, i]
            for j in range(n):
                if j == i or not row_i[j]:
                    continue
                row_j = matrix[j]
                for k in range(n):
                    if k == i or k == j:
                        continue
                    if row_j[k] and col_i[k]:
                        closed[i] = True
                        break
                if closed[i]:
                    break

    return float(closed.sum() / n)
