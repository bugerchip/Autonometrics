"""Shared empirical-entropy helpers used by multiple metrics.

Centralising these utilities keeps individual metric modules focused on
their own formula and prevents silent drift between implementations.
Only discrete integer arrays are supported; continuous signals must be
discretised upstream by the caller.
"""

from __future__ import annotations

import numpy as np

EPS: float = 1e-12


def shannon_entropy_from_counts(counts: np.ndarray) -> float:
    """Return the Shannon entropy (base 2) of an empirical count vector."""
    total = counts.sum()
    if total == 0:
        return 0.0
    probs = counts[counts > 0] / total
    return float(-np.sum(probs * np.log2(probs)))


def joint_entropy(*variables: np.ndarray) -> float:
    """Return the empirical Shannon entropy of a joint of 1D int arrays."""
    if not variables:
        return 0.0
    stacked = np.column_stack(variables)
    _, counts = np.unique(stacked, axis=0, return_counts=True)
    return shannon_entropy_from_counts(counts)


def normalized_entropy(x: np.ndarray) -> float:
    """Return ``H(x) / log2(n_unique)`` in ``[0.0, 1.0]``.

    A value of ``0`` means the variable is a constant and a value of
    ``1`` means it is uniformly distributed over its support. If the
    variable has a single unique value the normaliser would be zero, so
    we return ``0.0`` by convention (a constant variable has no
    normalised entropy, rather than an undefined one).
    """
    x_arr = np.asarray(x).ravel()
    if x_arr.size == 0:
        return 0.0
    unique_vals = np.unique(x_arr)
    if unique_vals.size <= 1:
        return 0.0
    _, counts = np.unique(x_arr, return_counts=True)
    h = shannon_entropy_from_counts(counts)
    h_max = float(np.log2(unique_vals.size))
    return h / h_max
