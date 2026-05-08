"""Distributed structural-memory ratio.

This metric answers a simple question: of the total structural memory
that lives in the joint (system, environment) trajectory, what
fraction is carried by the system itself?

.. math::

    M \\;=\\; \\frac{E(\\text{states})}{E(\\text{states}) + E(\\text{env})}

where ``E(.)`` is the Crutchfield excess entropy of a discrete
sequence, estimated by block-entropy saturation.

The ratio is dimensionless, lives in ``[0.0, 1.0]``, and shares the
``internal / total`` shape used by the rest of the package, so it is
directly comparable with the closure axis from
:func:`compute_albantakis`.

It replaces the previous absolute-bit ``compute_excess_entropy``
shipped in ``v0.3.x``: that function returned a magnitude rather
than a fraction, so the two axes lived in incompatible spaces. The
underlying excess-entropy computation is preserved as a private
helper and is now applied to both the system and the environment
before being normalised into a ratio.

References
----------
- Crutchfield, J. P., & Packard, N. H. (1983).
  *Symbolic dynamics of noisy chaos*. Physica D 7.
- Crutchfield, J. P., & Young, K. (1989).
  *Inferring statistical complexity*. Physical Review Letters 63.
- Feldman, D. P., & Crutchfield, J. P. (2002).
  *Measures of Statistical Complexity: Why?*. Physics Letters A 238.
- Grassberger, P. (1988). *Finite sample corrections to entropy and
  dimension estimates*. Physics Letters A 128.
"""

from __future__ import annotations

import math

import numpy as np

from autonometrics.metrics._entropy import EPS, shannon_entropy_from_counts


def _block_entropy(sequence: np.ndarray, block_length: int) -> float:
    """Empirical Shannon entropy of length-``block_length`` blocks."""
    n = sequence.size
    if block_length > n:
        return 0.0
    blocks = np.lib.stride_tricks.sliding_window_view(sequence, block_length)
    _, counts = np.unique(blocks, axis=0, return_counts=True)
    return shannon_entropy_from_counts(counts)


def _effective_block_length(n_samples: int, alphabet_size: int, requested: int) -> int:
    """Cap the working block length following a Grassberger-style rule.

    Ensures every possible block of the chosen length receives, on
    average, at least ten samples; this avoids the positive sampling
    bias that would otherwise inflate the empirical excess-entropy
    estimate on i.i.d. sequences.
    """
    alphabet = max(alphabet_size, 2)
    if n_samples < 20:
        ceiling = 2
    else:
        ceiling = int(math.floor(math.log(n_samples / 10.0) / math.log(alphabet)))
        ceiling = max(ceiling, 2)
    return min(requested, ceiling)


def _excess_entropy_of(sequence: np.ndarray, max_block_length: int) -> float:
    """Crutchfield excess entropy of a single 1D integer sequence, in bits."""
    seq = sequence.astype(np.int64, copy=False)
    if seq.size < 2:
        return 0.0
    alphabet_size = int(np.unique(seq).size)
    block_length = _effective_block_length(
        n_samples=seq.size,
        alphabet_size=alphabet_size,
        requested=max_block_length,
    )
    h_top = _block_entropy(seq, block_length)
    h_top_minus_one = _block_entropy(seq, block_length - 1)
    entropy_rate = h_top - h_top_minus_one
    excess = h_top - block_length * entropy_rate
    return float(max(excess, 0.0))


def compute_memory_endo_ratio(
    states: np.ndarray,
    env: np.ndarray,
    max_block_length: int = 8,
    min_length: int = 500,
    *,
    return_diagnostics: bool = False,
) -> float | tuple[float, dict[str, float]]:
    """Fraction of joint structural memory carried by the system.

    Parameters
    ----------
    states:
        1D integer array of discrete state labels of shape ``(T,)``.
    env:
        1D integer array of environment labels with the same length
        as ``states``.
    max_block_length:
        Upper bound on the block length used in the empirical
        block-entropy estimate. The actual working length is the
        smaller of this value and a Grassberger-style sample-based
        cap. Default ``8``.
    min_length:
        Minimum number of timesteps below which the estimator is
        considered unreliable and a ``ValueError`` is raised. Default
        ``500``.
    return_diagnostics:
        When ``True``, also returns a dictionary with the component
        excess-entropies (``e_states``, ``e_env``) used to form the
        ratio. Useful when downstream tooling needs to distinguish
        the magnitudes that produced a given ratio.

    Returns
    -------
    float
        A value in ``[0.0, 1.0]``. ``0.0`` means the structural
        memory of the joint trajectory lives entirely in the
        environment (or, by convention, both sequences carry no
        memory at all). ``1.0`` means it lives entirely in the
        system. Intermediate values report the fraction carried by
        the system.
    tuple[float, dict[str, float]]
        When ``return_diagnostics`` is ``True``.

    Raises
    ------
    ValueError
        If ``states`` and ``env`` disagree in length, if the series
        is shorter than ``min_length``, or if ``max_block_length`` is
        not at least ``2``.
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
            f"series too short for reliable memory-ratio estimation; "
            f"need at least {min_length} timesteps, got {states_arr.size}"
        )
    if max_block_length < 2:
        raise ValueError(f"max_block_length must be at least 2, got {max_block_length}")

    e_states = _excess_entropy_of(states_arr, max_block_length=max_block_length)
    e_env = _excess_entropy_of(env_arr, max_block_length=max_block_length)

    total = e_states + e_env
    if total <= EPS:
        score = 0.0
    else:
        score = float(np.clip(e_states / total, 0.0, 1.0))

    if return_diagnostics:
        diagnostics = {
            "e_states": float(e_states),
            "e_env": float(e_env),
        }
        return score, diagnostics
    return score
