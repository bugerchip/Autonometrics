"""Albantakis-style conditional-mutual-information measure of autonomy.

Simplified, pure-``numpy`` reimplementation of the ``A_m`` family of
measures surveyed in Albantakis (2021) and rooted in Bertschinger et
al. (2008). The quantity computed is the **normalised conditional
mutual information** between a system's state trajectory and itself,
conditioned on the environment:

.. math::

    A \\;=\\; \\frac{I(S_{t+1};\\,S_t \\mid E_t)}{H(S_{t+1} \\mid E_t)}

``A = 0`` means ``S_{t+1}`` is, given ``E_t``, independent of the
system's own previous state — all variation is driven from outside.
``A = 1`` means ``S_{t+1}`` is fully determined by ``S_t`` once the
environment is accounted for — the system "runs on its own rules".

References
----------
- Bertschinger, N., Olbrich, E., Ay, N., & Jost, J. (2008).
  *Autonomy: An Information-Theoretic Perspective*. BioSystems 91(2).
- Albantakis, L. (2021). *Quantifying the Autonomy of Structurally
  Diverse Automata: A Comparison of Candidate Measures*. Entropy 23(11).
"""

from __future__ import annotations

import numpy as np

from autonometrics.metrics._entropy import EPS, joint_entropy


def compute_albantakis(states: np.ndarray, env: np.ndarray) -> float:
    """Compute the normalised conditional-MI autonomy score.

    Parameters
    ----------
    states:
        1D integer array of discrete state labels of shape ``(T,)``.
    env:
        1D integer array of discrete environment labels of shape ``(T,)``.
        Must be the same length as ``states``; ``env[t]`` is the
        environment observed at timestep ``t``.

    Returns
    -------
    float
        A value in ``[0.0, 1.0]``. See module docstring for
        interpretation. The returned value is clipped into the unit
        interval to absorb small negative floating-point drift.

    Raises
    ------
    ValueError
        If ``states`` and ``env`` disagree in length, if there are fewer
        than two timesteps (no transitions to observe), or if
        ``H(S_{t+1} | E_t) == 0``, in which case the normalisation is
        undefined (for instance, when the system is a constant process
        or when the environment fully determines the next state).
    """
    states_arr = np.asarray(states).ravel()
    env_arr = np.asarray(env).ravel()

    if states_arr.shape != env_arr.shape:
        raise ValueError(
            f"states and env must have the same length: "
            f"got {states_arr.shape[0]} and {env_arr.shape[0]}"
        )
    if states_arr.size < 2:
        raise ValueError(
            f"need at least 2 timesteps to observe a transition; got {states_arr.size}"
        )

    states_int = states_arr.astype(np.int64, copy=False)
    env_int = env_arr.astype(np.int64, copy=False)

    prev_state = states_int[:-1]
    next_state = states_int[1:]
    env_t = env_int[:-1]

    h_z = joint_entropy(env_t)
    h_xz = joint_entropy(prev_state, env_t)
    h_yz = joint_entropy(next_state, env_t)
    h_xyz = joint_entropy(prev_state, next_state, env_t)

    h_next_given_env = h_yz - h_z
    h_next_given_prev_and_env = h_xyz - h_xz

    if h_next_given_env <= EPS:
        raise ValueError(
            "H(S_{t+1} | E_t) is zero: the next state has no conditional "
            "variability given the environment, so the normalised "
            "autonomy score is undefined."
        )

    mi_conditional = h_next_given_env - h_next_given_prev_and_env
    normalised = mi_conditional / h_next_given_env
    return float(np.clip(normalised, 0.0, 1.0))
