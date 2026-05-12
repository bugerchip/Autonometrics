"""Lee & McShea-style perturbation persistence as a structural autonomy proxy.

This module operationalises the fourth PBA axis: a **structural
autonomous-motivation proxy (RAI-style)** built around the question
*"if the system is perturbed, does it return to its own trajectory?"*

Conceptual lineage
------------------
The conceptual core comes from Lee & McShea (2020),
*"Operationalizing Goal Directedness"* (Philosophy, Theory, and
Practice in Biology 12), where **persistence** is defined as

    "the tendency for an entity on a trajectory toward a goal to
     return to that trajectory following perturbations"

and quantified as :math:`P = (G/N - R) / (1 - R)`, with ``G`` the
number of "good moves" (those that reduce the distance to the goal),
``N`` the total number of moves, and ``R`` the chance probability of
a good move under random movement.

This module preserves Lee & McShea's intuition (*persist toward a
preferred trajectory after perturbation*) while making four
adaptations needed to apply the metric to the package's adapter zoo,
which lacks externally specified goals and uses high-dimensional
discrete state vectors. The four adaptations are documented in
:doc:`docs/RAI` under "Differences from the original Lee & McShea
formulation":

1. **Implicit goal.** The system's own *unperturbed* focal trajectory
   is treated as the implicit goal; a "good move" is any
   post-perturbation step whose focal value matches the unperturbed
   focal value at the same time index.
2. **Hamming distance.** Comparison uses focal-state Hamming
   distance (mismatch indicator) rather than Euclidean distance,
   which is the natural metric for discrete-alphabet trajectories.
3. **Computed baseline.** The chance baseline ``R`` (or its distance
   counterpart ``d_ref``) is computed empirically per adapter from
   the marginal state distribution, rather than being assumed
   uniform; this matches the heterogeneous discrete state spaces
   the package supports.
4. **Multi-perturbation averaging.** Each measurement averages over
   ``n_perturbations`` independent perturbation times to yield a
   population-level estimator robust to the specific time at which
   the perturbation lands.

Score
-----
The implementation uses the distance form of Lee & McShea's
expression, which is equivalent to the ratio form under the
conventions above:

.. math::

    \\text{persistence} \\;=\\;
    \\operatorname{clip}\\!\\left(
        1 \\;-\\; \\bar d \\,/\\, d_{\\text{ref}}, \\;
        0, \\, 1
    \\right)

where :math:`\\bar d` is the mean Hamming distance between the
perturbed and the unperturbed focal trajectories over a horizon of
``horizon`` steps, averaged over ``n_perturbations`` independent
perturbation times, and :math:`d_{\\text{ref}}` is the empirical
reference scale ``1 - sum(p_a ** 2)`` (the complement of the
collision probability of two i.i.d. draws from the focal marginal
distribution). ``persistence = 1`` means perturbations are absorbed
perfectly; ``persistence = 0`` means perturbations propagate as much
as two independent random trajectories of the same alphabet would.

Adapter contract
----------------
The metric does not run the system itself. It expects a callable
``replay_fn(t_star, n_steps, rng)`` that returns the
post-perturbation focal trajectory of length ``n_steps`` starting
from a single-element perturbation applied to the system's full
internal state at time ``t_star``. Each adapter implements this
natively; adapters that cannot replay (e.g. CSV-only trajectories)
do not expose the method and the orchestrator records ``None`` for
this axis.

The protocol-level method is
``AutonomySystem.replay_from_perturbation(t_star, n_steps, rng=None)``
and is documented in :class:`autonometrics.core.AutonomySystem`.

Independence-by-design
----------------------
This module is **deliberately information-theory-free** and
**graph-free**. It imports only ``numpy`` and works exclusively from
focal trajectories and a replay callable. In particular, it does
**not** import any of:

- ``autonometrics.metrics._entropy``
- ``autonometrics.metrics.albantakis``
- ``autonometrics.metrics.memory_ratio``
- ``autonometrics.metrics.constraint_closure``
- third-party information-theory toolkits (``pyinform``, ``dit``).

This guarantees that any empirical correlation found between the
persistence axis and the three axes already shipped (closure,
memory, constraint-closure) is structural, not algebraic. The
PBA document (:doc:`docs/PBA`) makes that independence-by-design a
hard requirement before any cross-axis correlation can count as
evidence for or against the atlas claim.

References
----------
- Lee, J. G., & McShea, D. W. (2020). *Operationalizing Goal
  Directedness: An Empirical Route to Advancing a Philosophical
  Discussion*. Philosophy, Theory, and Practice in Biology 12(5).
- Albantakis, L. (2021). *Quantifying the Autonomy of Structurally
  Diverse Automata: A Comparison of Candidate Measures*. Entropy
  23(11), 1415.
- Ashby, W. R. (1947). *Principles of the Self-Organizing Dynamic
  System*. Journal of General Psychology 37(2), 125 — 128.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

PerturbationReplayFn = Callable[..., np.ndarray]
"""Callable signature: ``(t_star: int, n_steps: int, rng=None) -> np.ndarray``.

Adapters expose this as a method named ``replay_from_perturbation``
on the :class:`AutonomySystem` instance.
"""

_DEFAULT_N_PERTURBATIONS = 32
_DEFAULT_HORIZON = 64
_DEFAULT_SEED = 0
_MIN_DREF = 1e-6


def compute_rai_proxy_persistence(
    states: np.ndarray,
    env: np.ndarray,
    replay_fn: PerturbationReplayFn,
    *,
    n_perturbations: int = _DEFAULT_N_PERTURBATIONS,
    horizon: int = _DEFAULT_HORIZON,
    rng: np.random.Generator | None = None,
    return_diagnostics: bool = False,
) -> float | tuple[float, dict[str, float]]:
    """Compute the Lee & McShea-style perturbation-persistence proxy.

    Parameters
    ----------
    states:
        1-D integer ``np.ndarray`` of focal-state observations.
        Must contain at least ``horizon + 2`` samples and have a
        non-degenerate marginal distribution (at least two distinct
        values).
    env:
        1-D integer ``np.ndarray`` of the same length as ``states``.
        Currently unused by the score itself; accepted for protocol
        symmetry with the other trajectory-based metrics so that
        :class:`autonometrics.Autonometer` can dispatch uniformly.
    replay_fn:
        Adapter-supplied callable. ``replay_fn(t_star, n_steps, rng)``
        must return a 1-D integer ``np.ndarray`` of length
        ``n_steps`` containing the focal trajectory observed
        starting at time ``t_star + 1`` after a single-element
        perturbation has been applied to the system's full internal
        state at time ``t_star``. Adapters that cannot replay must
        not expose this callable (the orchestrator records ``None``
        for the metric in that case).
    n_perturbations:
        Number of independent perturbation trials. Defaults to ``32``.
    horizon:
        Number of post-perturbation steps each trial follows.
        Defaults to ``64``.
    rng:
        Optional ``numpy.random.Generator`` for reproducibility.
        Defaults to ``np.random.default_rng(0)``.
    return_diagnostics:
        When ``True``, also returns a dictionary with the component
        magnitudes (``mean_hamming``, ``d_ref``) used to form the
        score. Useful when downstream tooling needs to inspect the
        empirical perturbation response and the chance baseline
        separately from the normalised ratio.

    Returns
    -------
    float
        A value in ``[0.0, 1.0]``. ``1.0`` means the system absorbs
        perturbations perfectly (perturbed trajectories agree with
        the unperturbed trajectory at every step beyond ``t_star``).
        ``0.0`` means perturbations propagate as much as two
        independent random trajectories of the same focal alphabet.
    tuple[float, dict[str, float]]
        When ``return_diagnostics`` is ``True``.

    Raises
    ------
    ValueError
        If ``states`` and ``env`` have different lengths, the
        trajectory is too short for the requested ``horizon``, the
        focal marginal is degenerate (single-symbol or near-constant),
        or ``n_perturbations`` / ``horizon`` are non-positive.

    Notes
    -----
    The score is computed in the **distance form** of Lee & McShea's
    persistence expression. Setting :math:`\\bar d` to the mean
    Hamming mismatch and :math:`d_{\\text{ref}} = 1 - \\sum_a p_a^2`
    (the complement of the collision probability of two i.i.d. draws
    from the focal marginal), the score reduces to

    .. math::

        \\operatorname{persistence}
        \\;=\\; \\operatorname{clip}\\!\\bigl(
            1 - \\bar d \\,/\\, d_{\\text{ref}}, \\, 0, \\, 1
        \\bigr).

    For binary balanced trajectories ``d_ref`` is approximately
    ``0.5``; for any other empirical marginal it is computed from
    the data and exposed implicitly through the score.
    """
    states_arr = np.asarray(states).ravel()
    env_arr = np.asarray(env).ravel()
    if states_arr.shape != env_arr.shape:
        raise ValueError(
            "states and env must have the same length; got "
            f"{states_arr.shape[0]} and {env_arr.shape[0]}"
        )
    if not np.issubdtype(states_arr.dtype, np.integer):
        raise ValueError(f"states must be integer-valued; got dtype {states_arr.dtype}")

    n = states_arr.size
    if n_perturbations <= 0:
        raise ValueError(f"n_perturbations must be positive; got {n_perturbations}")
    if horizon <= 0:
        raise ValueError(f"horizon must be positive; got {horizon}")
    if n < horizon + 2:
        raise ValueError(
            f"trajectory too short for persistence: need at least horizon + 2 = "
            f"{horizon + 2} samples, got {n}"
        )

    counts = np.bincount(states_arr.astype(np.int64))
    p = counts / counts.sum()
    d_ref = 1.0 - float(np.sum(p**2))
    if d_ref <= _MIN_DREF:
        raise ValueError(
            f"focal marginal is (near-)constant; persistence is undefined (d_ref = {d_ref:.2e})"
        )

    rng = rng if rng is not None else np.random.default_rng(_DEFAULT_SEED)
    last_t_star = n - horizon - 1
    if last_t_star < 1:
        raise ValueError(
            "trajectory leaves no room for perturbation; need at least horizon + 2 samples"
        )

    distances = np.empty(n_perturbations, dtype=float)
    for trial in range(n_perturbations):
        t_star = int(rng.integers(0, last_t_star))
        perturbed = np.asarray(replay_fn(t_star, horizon, rng=rng)).ravel()
        if perturbed.shape[0] != horizon:
            raise ValueError(f"replay_fn returned {perturbed.shape[0]} samples, expected {horizon}")
        baseline = states_arr[t_star + 1 : t_star + 1 + horizon]
        if baseline.shape[0] != horizon:
            raise ValueError(f"baseline slice has {baseline.shape[0]} samples, expected {horizon}")
        distances[trial] = float(np.mean(perturbed != baseline))

    d_bar = float(np.mean(distances))
    score = 1.0 - d_bar / d_ref
    score = float(np.clip(score, 0.0, 1.0))

    if return_diagnostics:
        diagnostics = {
            "mean_hamming": float(d_bar),
            "d_ref": float(d_ref),
        }
        return score, diagnostics
    return score
