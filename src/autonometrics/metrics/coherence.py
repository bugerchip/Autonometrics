"""Theil-U-style coherence proxy on declared / executed trajectories.

This module operationalises the fifth PBA axis: a **structural
coherence proxy (CBA-style)** built around the question
*"how much of the executed trajectory is predictable from the
declared one?"*

Conceptual lineage
------------------
The phenomenon — the gap between what a system declares and
what it does — has been studied under different names across
multiple traditions:

- **Aristotle**, *Ethica Nicomachea* VII: *akrasia* as the
  failure of action to follow judgement.
- **Festinger (1957)**, *A Theory of Cognitive Dissonance*:
  the dissonance ratio ``D / (D + C)``, the earliest explicit
  ``[0, 1]`` measurement of the gap.
- **Sheeran (2002)**, intention–behaviour gap meta-analysis
  (n = 82,107 across 422 studies): intentions explain
  ``~28%`` of the variance in behaviour.
- **Searle (1979)**, commissives: speech acts whose direction
  of fit is *world-to-word*.
- **PhilArchive (2024)**, *Coherence-Based Alignment*: the
  contemporary frame that this module borrows the name from.
- **Lanham et al. (2023)** and **Turpin et al. (2023)**:
  CoT-faithfulness work on language models, the
  AI-alignment instance of the same gap.

The package's CBA axis is **one operationalisation among
many**, with explicit lineage and explicit limits. It is *not*
a re-implementation of any specific source. Full design
rationale, candidate alternatives and pre-registered
falsification thresholds live in :doc:`docs/CBA`.

Score
-----
The implementation uses **Theil's U** (uncertainty
coefficient) on the joint of two parallel discrete
trajectories ``D`` (declared) and ``E`` (executed):

.. math::

    \\text{cba\\_theil\\_u}
    \\;=\\;
    \\operatorname{clip}\\!\\left(
        \\frac{I(D; E)}{H(D)}, \\, 0, \\, 1
    \\right)

where ``H(D)`` is the Shannon entropy of the declared marginal
and ``I(D; E) = H(D) + H(E) - H(D, E)`` is the mutual
information of the joint. All entropies use a **Miller-Madow**
bias correction. ``cba_theil_u = 1`` means the executed
trajectory is fully predictable from the declared one (the
declaration's uncertainty is fully resolved by knowing the
execution); ``cba_theil_u = 0`` means execution is statistically
independent of declaration.

Note on bijections
~~~~~~~~~~~~~~~~~~
A non-identity deterministic bijection ``E = π(D)`` scores
``1.0`` on ``cba_theil_u`` (declared side perfectly predicts
executed side), even though ``D`` and ``E`` never agree
pointwise. This is the textbook behaviour of Theil's U and is
*correct* under the "predictability" reading of coherence,
but can be counter-intuitive under a "match" reading. The
companion diagnostic ``cba_match_rate`` (the fraction of
timesteps with ``D_t == E_t``) disambiguates the case: a
configuration where ``cba_theil_u ≈ 1`` and
``cba_match_rate ≈ 0`` flags a *systematic substitution*
(informative declaration, mismatched alphabet), not a
coherence failure. Pass ``return_diagnostics=True`` to receive
the diagnostic alongside the score.

Adapter contract
----------------
The metric expects a system that exposes
``get_declared_executed()`` returning a tuple
``(declared, executed)`` of integer 1-D arrays of the same
shape. Adapters that have no declarative layer (e.g.
``SimpleAutomaton``, cellular automata, Boolean networks) must
not expose the method (or must return ``None``); the
orchestrator records ``None`` for this axis in that case. CBA
is by design the narrowest axis in the atlas — only systems
with a meaningful declarative layer are scored.

Independence-by-design
----------------------
This module is **deliberately information-theory-toolkit-free**
and **graph-free**. It imports only ``numpy`` and the standard
library. In particular, it does **not** import any of:

- ``autonometrics.metrics._entropy``
- ``autonometrics.metrics.albantakis``
- ``autonometrics.metrics.memory_ratio``
- ``autonometrics.metrics.constraint_closure``
- ``autonometrics.metrics.persistence``
- third-party information-theory toolkits (``pyinform``, ``dit``).

Shannon entropy and Miller-Madow are reimplemented locally
(~10 lines) so that any cross-axis correlation observed on the
five-axis benchmark is structural, not algebraic. This mirrors
the discipline applied to ``persistence`` in
``metrics/persistence.py``.

References
----------
- Theil, H. (1970). On the Estimation of Relationships
  Involving Qualitative Variables. *American Journal of
  Sociology*, 76(1), 103–154.
- Miller, G. A. (1955). Note on the bias of information
  estimates. In *Information Theory in Psychology*.
- Festinger, L. (1957). *A Theory of Cognitive Dissonance*.
- Sheeran, P. (2002). Intention–Behaviour Relations.
  *European Review of Social Psychology*, 12(1), 1–36.
- PhilArchive (2024). *Coherence-Based Alignment*.
"""

from __future__ import annotations

import warnings

import numpy as np

_LOW_N_DEFAULT = 100
_LN2 = float(np.log(2.0))


def _remap_to_dense(arr: np.ndarray) -> tuple[np.ndarray, int]:
    """Remap arbitrary integer alphabet to ``range(K)`` and return ``K``.

    Stable across calls for the same input distribution; only used
    internally to keep the joint-histogram bookkeeping cheap.
    """
    unique, inverse = np.unique(arr, return_inverse=True)
    return inverse.astype(np.int64, copy=False), int(unique.size)


def _shannon_entropy_mm(arr: np.ndarray) -> float:
    """Shannon entropy in bits with Miller-Madow bias correction.

    The plug-in estimator is biased low; the Miller-Madow correction
    adds ``(K - 1) / (2 * T * ln 2)`` where ``K`` is the number of
    *observed* (non-empty) symbols and ``T`` is the sample size.
    """
    n = int(arr.size)
    if n == 0:
        return 0.0
    _, counts = np.unique(arr, return_counts=True)
    if counts.size <= 1:
        return 0.0
    p = counts / n
    h_plugin = float(-np.sum(p * np.log2(p)))
    k_observed = int((counts > 0).sum())
    correction = (k_observed - 1) / (2.0 * n * _LN2)
    return h_plugin + correction


def _joint_entropy_mm(x: np.ndarray, y: np.ndarray) -> float:
    """Miller-Madow-corrected Shannon entropy of the joint ``(x, y)``."""
    n = int(x.size)
    if n == 0:
        return 0.0
    pair = np.column_stack((x, y))
    _, counts = np.unique(pair, axis=0, return_counts=True)
    if counts.size <= 1:
        return 0.0
    p = counts / n
    h_plugin = float(-np.sum(p * np.log2(p)))
    k_observed = int((counts > 0).sum())
    correction = (k_observed - 1) / (2.0 * n * _LN2)
    return h_plugin + correction


def _match_rate(declared: np.ndarray, executed: np.ndarray) -> float:
    """Fraction of timesteps with pointwise equality (Festinger-style)."""
    if declared.size == 0:
        return 0.0
    return float(np.mean(declared == executed))


def compute_cba_theil_u(
    declared: np.ndarray,
    executed: np.ndarray,
    *,
    low_n_threshold: int = _LOW_N_DEFAULT,
    return_diagnostics: bool = False,
) -> float | tuple[float, dict[str, float]]:
    """Compute the information-theoretic CBA proxy (Theil-U style).

    Parameters
    ----------
    declared:
        1-D integer ``np.ndarray`` of the declared trajectory.
    executed:
        1-D integer ``np.ndarray`` of the executed trajectory.
        Must have the same shape and dtype family as ``declared``.
    low_n_threshold:
        Sample size below which a ``RuntimeWarning`` is raised to
        flag substantial estimator bias. Defaults to ``100``;
        Miller-Madow is still applied at all ``T``.
    return_diagnostics:
        When ``True``, also returns a dictionary with the companion
        diagnostics (``match_rate``, ``H_D``, ``H_E``, ``MI``, ``T``).
        The match rate disambiguates the bijection case (high
        Theil-U, low match rate) from the genuine-coherence case
        (high Theil-U, high match rate).

    Returns
    -------
    float
        A value in ``[0.0, 1.0]``. ``1.0`` means knowing the
        executed trajectory removes all uncertainty about the
        declared one (deterministic predictability of ``E`` from
        ``D``). ``0.0`` means executed and declared are
        statistically independent. By convention, when ``H(D) = 0``
        (constant declared trajectory) the score is ``0.0`` —
        there is no declared-side uncertainty to resolve.
    tuple[float, dict[str, float]]
        When ``return_diagnostics`` is ``True``.

    Raises
    ------
    ValueError
        If shapes differ, dtypes are non-integer, or the input is
        empty.

    Notes
    -----
    Both inputs are remapped to a dense ``range(K)`` integer
    alphabet before histogramming. The mapping is internal: the
    remap is purely for histogram bookkeeping and does not change
    the score (entropies and mutual information are alphabet-
    invariant). See the module docstring for the bijection
    caveat.
    """
    d = np.asarray(declared)
    e = np.asarray(executed)
    if d.shape != e.shape:
        raise ValueError(
            f"declared and executed must have the same shape; got {d.shape} and {e.shape}"
        )
    if d.ndim != 1:
        raise ValueError(f"declared must be 1-D; got shape {d.shape}")
    if d.size == 0:
        raise ValueError("declared and executed must be non-empty")
    if not np.issubdtype(d.dtype, np.integer):
        raise ValueError(f"declared must be integer-valued; got dtype {d.dtype}")
    if not np.issubdtype(e.dtype, np.integer):
        raise ValueError(f"executed must be integer-valued; got dtype {e.dtype}")

    n = int(d.size)
    if n < low_n_threshold:
        warnings.warn(
            f"CBA computed at T={n} < {low_n_threshold}; "
            "Miller-Madow correction is applied but estimator bias "
            "may still be substantial",
            RuntimeWarning,
            stacklevel=2,
        )

    d_dense, _ = _remap_to_dense(d)
    e_dense, _ = _remap_to_dense(e)

    h_d = _shannon_entropy_mm(d_dense)
    if h_d <= 0.0:
        score = 0.0
        if return_diagnostics:
            diagnostics = {
                "match_rate": _match_rate(d, e),
                "H_D": 0.0,
                "H_E": _shannon_entropy_mm(e_dense),
                "MI": 0.0,
                "T": float(n),
            }
            return score, diagnostics
        return score

    h_e = _shannon_entropy_mm(e_dense)
    h_de = _joint_entropy_mm(d_dense, e_dense)
    mi = h_d + h_e - h_de
    raw = mi / h_d
    score = float(np.clip(raw, 0.0, 1.0))

    if return_diagnostics:
        diagnostics = {
            "match_rate": _match_rate(d, e),
            "H_D": float(h_d),
            "H_E": float(h_e),
            "MI": float(mi),
            "T": float(n),
        }
        return score, diagnostics
    return score
