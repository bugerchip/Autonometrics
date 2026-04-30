"""Fernandez-Gershenson autopoietic ratio.

Implementation of the autopoiesis measure from Fernandez, Maldonado &
Gershenson (2014), *Information Measures of Complexity, Emergence,
Self-organization, Homeostasis, and Autopoiesis*:

.. math::

    A \\;=\\; \\frac{C(\\text{states})}{C(\\text{env})}

where the complexity ``C`` of a discrete variable is the symmetrised
form used by Lopez-Ruiz, Mancini & Calbet,

.. math::

    C(x) \\;=\\; 4 \\cdot E(x) \\cdot (1 - E(x))

with ``E(x) = H(x) / log2(|supp(x)|)`` the normalised Shannon entropy.

``C(x)`` lives in ``[0, 1]`` with a maximum at ``E = 0.5`` (balanced
order and disorder), so the ratio ``A`` lives in ``[0, +inf)``:

- ``A < 1`` means the environment is *more* complex than the system,
  which points to an externally driven / heteronomous regime.
- ``A ≈ 1`` means system and environment are similarly complex.
- ``A > 1`` means the system is more complex than its environment,
  the signature of an autopoietic / self-producing regime.

The ratio is **not clipped**: a large autopoietic regime should not be
squashed to one by the instrument. Consumers that want a bounded score
can apply ``min(A, 1.0)`` themselves.

References
----------
- Fernandez, N., Maldonado, C., & Gershenson, C. (2014).
  *Information Measures of Complexity, Emergence, Self-organization,
  Homeostasis, and Autopoiesis*. In: Guided Self-Organization:
  Inception, Emergence, Complexity and Computation, vol. 9. Springer.
- Gershenson, C., & Fernandez, N. (2012). *Complexity and information:
  Measuring emergence, self-organization, and homeostasis at multiple
  scales*. Complexity 18(2).
"""

from __future__ import annotations

import numpy as np

from autonometrics.metrics._entropy import EPS, normalized_entropy


def _complexity(x: np.ndarray) -> float:
    """Return the Lopez-Ruiz-Mancini-Calbet complexity of ``x`` in ``[0, 1]``."""
    e = normalized_entropy(x)
    return 4.0 * e * (1.0 - e)


def compute_autopoietic_ratio(states: np.ndarray, env: np.ndarray) -> float:
    """Compute the Fernandez-Gershenson autopoietic ratio.

    Parameters
    ----------
    states:
        1D integer array of discrete state labels of shape ``(T,)``.
    env:
        1D integer array of discrete environment labels of shape ``(T,)``.
        Must be the same length as ``states``.

    Returns
    -------
    float
        A non-negative value; values above ``1.0`` mean the system is
        more complex than its environment. The caller is responsible
        for any clipping or downstream normalisation.

    Raises
    ------
    ValueError
        If ``states`` and ``env`` disagree in length, if there are
        fewer than two timesteps, or if the environment has zero
        complexity (constant or maximally ordered), in which case the
        ratio is undefined.
    """
    states_arr = np.asarray(states).ravel()
    env_arr = np.asarray(env).ravel()

    if states_arr.shape != env_arr.shape:
        raise ValueError(
            f"states and env must have the same length: "
            f"got {states_arr.shape[0]} and {env_arr.shape[0]}"
        )
    if states_arr.size < 2:
        raise ValueError(f"need at least 2 timesteps to observe complexity; got {states_arr.size}")

    c_states = _complexity(states_arr)
    c_env = _complexity(env_arr)

    if c_env <= EPS:
        raise ValueError(
            "C(env) is zero: the environment has no complexity "
            "(constant or single-valued), so the autopoietic ratio "
            "is undefined."
        )

    return float(c_states / c_env)
