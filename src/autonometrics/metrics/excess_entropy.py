"""Crutchfield excess entropy as a structural-memory measure.

Excess entropy ``E`` answers a simple question: how many bits of the
system's past are useful for predicting its future? It is zero for
constant or i.i.d. noise processes, ``log2(p)`` for a deterministic
period-``p`` cycle, and generally positive for sequences with
long-range temporal structure.

This replaces the previous LMC-based autopoietic ratio, which was
shown by Feldman & Crutchfield (2002) to collapse to zero on
structured ordered systems such as deterministic cycles.

The estimator used here is the *block-entropy saturation* form:

.. math::

    E \\;=\\; H(L) - L \\cdot h_\\mu

where ``H(L)`` is the empirical Shannon entropy of blocks of length
``L`` in the sequence and
``h_\\mu = H(L) - H(L - 1)`` is the asymptotic entropy rate.

The working block length ``L`` is capped by a Schurmann-Grassberger
rule of thumb so that every possible block gets on average at least
ten samples, avoiding the positive sampling bias that would otherwise
inflate the estimate on i.i.d. sequences.

The metric only uses the system's state trajectory: the ``env``
argument is accepted for registry-compatibility with other metrics but
is not consulted. The return value is non-negative (any small negative
numerical drift is clipped to zero).

References
----------
- Crutchfield, J. P., & Packard, N. H. (1983).
  *Symbolic dynamics of noisy chaos*. Physica D 7.
- Crutchfield, J. P., & Young, K. (1989).
  *Inferring statistical complexity*. Physical Review Letters 63.
- Feldman, D. P., & Crutchfield, J. P. (2002).
  *Measures of Statistical Complexity: Why?*.
  Physics Letters A 238 (motivates retiring LMC for structure).
- Grassberger, P. (1988). *Finite sample corrections to entropy and
  dimension estimates*. Physics Letters A 128.
"""

from __future__ import annotations

import math

import numpy as np

from autonometrics.metrics._entropy import shannon_entropy_from_counts


def _block_entropy(sequence: np.ndarray, block_length: int) -> float:
    """Return the empirical Shannon entropy of length-``block_length`` blocks."""
    n = sequence.size
    if block_length > n:
        return 0.0
    blocks = np.lib.stride_tricks.sliding_window_view(sequence, block_length)
    _, counts = np.unique(blocks, axis=0, return_counts=True)
    return shannon_entropy_from_counts(counts)


def _effective_block_length(n_samples: int, alphabet_size: int, requested: int) -> int:
    """Cap the block length so every possible block gets ~10 samples on average.

    This Grassberger-style rule keeps the empirical entropy estimate
    unbiased enough that the excess-entropy saturation formula does
    not pick up phantom structure from under-sampling.
    """
    alphabet = max(alphabet_size, 2)
    if n_samples < 20:
        ceiling = 2
    else:
        ceiling = int(math.floor(math.log(n_samples / 10.0) / math.log(alphabet)))
        ceiling = max(ceiling, 2)
    return min(requested, ceiling)


def compute_excess_entropy(
    states: np.ndarray,
    env: np.ndarray,
    max_block_length: int = 8,
    min_length: int = 500,
) -> float:
    """Compute the Crutchfield excess entropy of ``states``.

    Parameters
    ----------
    states:
        1D integer array of discrete state labels of shape ``(T,)``.
    env:
        1D integer array of environment labels; accepted for
        registry-compatibility with other metrics but not used by this
        estimator. Must have the same length as ``states``.
    max_block_length:
        Upper bound for the block length used in the empirical
        entropy estimate. The actual working length is the smaller of
        this value and a sample-based cap (see notes). Default ``8``.
    min_length:
        Minimum number of timesteps below which the estimator is
        considered unreliable and a ``ValueError`` is raised. Default
        ``500``.

    Returns
    -------
    float
        A non-negative value in bits. Constant sequences and i.i.d.
        noise both return a value close to zero; a deterministic
        period-``p`` cycle returns a value close to ``log2(p)``.

    Raises
    ------
    ValueError
        If ``states`` and ``env`` disagree in length, if the series
        is shorter than ``min_length``, or if ``max_block_length`` is
        not at least ``2``.

    Notes
    -----
    The working block length is capped so that
    ``alphabet_size ** L <= n_samples / 10``, following a
    Grassberger-style rule of thumb. This prevents positive sampling
    bias from inflating the score on random sequences.
    """
    states_arr = np.asarray(states).ravel()
    env_arr = np.asarray(env).ravel()

    if states_arr.shape != env_arr.shape:
        raise ValueError(
            f"states and env must have the same length: "
            f"got {states_arr.shape[0]} and {env_arr.shape[0]}"
        )
    if states_arr.size < min_length:
        raise ValueError(
            f"series too short for reliable excess-entropy estimation; "
            f"need at least {min_length} timesteps, got {states_arr.size}"
        )
    if max_block_length < 2:
        raise ValueError(f"max_block_length must be at least 2, got {max_block_length}")

    states_int = states_arr.astype(np.int64, copy=False)
    alphabet_size = int(np.unique(states_int).size)

    block_length = _effective_block_length(
        n_samples=states_int.size,
        alphabet_size=alphabet_size,
        requested=max_block_length,
    )

    h_top = _block_entropy(states_int, block_length)
    h_top_minus_one = _block_entropy(states_int, block_length - 1)
    entropy_rate = h_top - h_top_minus_one

    excess = h_top - block_length * entropy_rate
    return float(max(excess, 0.0))
