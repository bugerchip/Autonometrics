"""Reference adapter for the CBA (coherence) axis.

``PromisedCycle`` is the canonical CBA-positive substrate: a
periodic schedule (the *declaration*) paired with a noisy
execution (the *execution*). It exists so the fifth PBA axis
has at least one adapter that exposes a non-trivial
declarative layer; ECAs, Boolean networks, simple automata and
periodic cycles do not, and the orchestrator records ``None``
for the CBA axis on those by design.

The adapter has two modes:

- ``random_noise``. With probability ``p_noise`` per step, the
  executed symbol is replaced by a uniformly drawn symbol from
  the **full alphabet** (including, with probability
  ``1/alphabet``, the declared symbol itself). This gives the
  expected behaviour ``executed ⟂ declared`` at ``p_noise = 1``,
  i.e. statistical independence of the two trajectories. Used to
  sweep CBA scores from ``1.0`` (at ``p_noise = 0``) down to
  ``≈ 0.0`` (at ``p_noise = 1``).
- ``adversarial_shift``. The executed symbol is always the
  declared symbol shifted by ``+1 (mod alphabet)``. A
  deterministic non-identity bijection: declared perfectly
  predicts executed, but they never agree pointwise. The
  textbook case where ``cba_theil_u ≈ 1`` and
  ``cba_match_rate ≈ 0``.

In addition to ``p_noise``, the adapter optionally accepts
``p_env`` — an **independent** per-step replacement probability
that perturbs the *declared* trajectory itself before the
executed channel is built. ``p_env`` exists so a single
``PromisedCycle`` instance can be driven by **two independent
sources of variability** (one on the declaration, one on the
execution). Sweeping both axes is the cleanest way to test
whether observed correlations between trajectory- and
declaration-based metrics (e.g. closure × coherence) come from
shared structure or merely from a single shared driver. When
``p_env = 0`` the adapter behaves byte-for-byte as before.

The class also implements the standard ``AutonomySystem``
methods (``get_state_history``, ``get_env_history``) so that
the same instance is a valid input to the four shipped
trajectory- and graph-based metrics. Closure / memory /
constraint / persistence on a ``PromisedCycle`` are well-defined
and can be reported alongside CBA on the five-axis benchmark.

Design rationale and per-mode predictions live in
:doc:`docs/CBA` (sections "Per-adapter predictions" and
"Falsification thresholds").
"""

from __future__ import annotations

import numpy as np

_MODE_RANDOM = "random_noise"
_MODE_ADVERSARIAL = "adversarial_shift"
_VALID_MODES = (_MODE_RANDOM, _MODE_ADVERSARIAL)


class PromisedCycle:
    """Periodic declaration paired with a noisy or shifted execution.

    Parameters
    ----------
    length:
        Total number of timesteps in both trajectories.
    period:
        Period of the declared cycle. Must satisfy
        ``1 <= period <= alphabet``.
    alphabet:
        Number of distinct symbols in the declared cycle. Must
        be at least ``2``.
    mode:
        Either ``"random_noise"`` (default) or
        ``"adversarial_shift"``. See module docstring.
    p_noise:
        Per-step replacement probability on the **executed**
        channel in ``random_noise`` mode. Ignored in
        ``adversarial_shift`` mode. Must lie in ``[0.0, 1.0]``.
    p_env:
        Per-step replacement probability on the **declared**
        channel, sampled from a separate sub-stream of the same
        seed so it is statistically independent of the executed
        noise. With probability ``p_env`` the declared symbol at
        a given step is replaced by a uniformly drawn alphabet
        symbol; otherwise the periodic cycle value is kept.
        ``p_env = 0`` (the default) preserves the original pure
        cycle and the byte-for-byte behaviour of older versions.
        Must lie in ``[0.0, 1.0]``.
    seed:
        Reproducibility seed for both noise processes.
    """

    def __init__(
        self,
        *,
        length: int,
        period: int,
        alphabet: int,
        mode: str = _MODE_RANDOM,
        p_noise: float = 0.0,
        p_env: float = 0.0,
        seed: int = 0,
    ) -> None:
        if mode not in _VALID_MODES:
            raise ValueError(f"Unknown mode {mode!r}; expected one of {_VALID_MODES}")
        if length < 2:
            raise ValueError(f"length must be at least 2; got {length}")
        if alphabet < 2:
            raise ValueError(f"alphabet must be at least 2; got {alphabet}")
        if not 1 <= period <= alphabet:
            raise ValueError(
                f"period must lie in [1, alphabet={alphabet}]; got {period}"
            )
        if not 0.0 <= p_noise <= 1.0:
            raise ValueError(f"p_noise must lie in [0.0, 1.0]; got {p_noise}")
        if not 0.0 <= p_env <= 1.0:
            raise ValueError(f"p_env must lie in [0.0, 1.0]; got {p_env}")

        self._length = int(length)
        self._period = int(period)
        self._alphabet = int(alphabet)
        self._mode = mode
        self._p_noise = float(p_noise)
        self._p_env = float(p_env)
        self._seed = int(seed)

        self._declared: np.ndarray | None = None
        self._executed: np.ndarray | None = None

    @classmethod
    def simple(
        cls,
        *,
        p_noise: float = 0.1,
        seed: int = 0,
        length: int = 600,
    ) -> PromisedCycle:
        """Build a typical ``PromisedCycle`` with one knob (``p_noise``).

        Convenience factory for casual use. Picks defaults that:

        - keep ``length`` above the 500-timestep floor required by the
          ``memory`` axis, so all four trajectory-based axes (closure,
          memory, persistence, coherence) yield non-trivial scores;
        - use a small alphabet (``alphabet = 4``) and matching cycle
          period (``period = 4``) so the declared trajectory walks
          through every symbol exactly once per period;
        - default to ``p_noise = 0.1``, a mid-low noise level where
          ``cba_theil_u`` is well below 1 but well above the noise
          floor — useful as a sanity-check baseline.

        The verbose ``PromisedCycle(...)`` constructor remains the
        only path for non-default ``period``, ``alphabet``, ``mode``
        or ``p_env`` values.

        Parameters
        ----------
        p_noise:
            Per-step replacement probability on the executed channel.
            Defaults to ``0.1``.
        seed:
            Reproducibility seed. Defaults to ``0``.
        length:
            Total number of timesteps. Defaults to ``600``, which
            comfortably clears the 500-timestep minimum the
            ``memory`` axis requires.

        Returns
        -------
        PromisedCycle
            A configured instance ready to be passed to
            :class:`autonometrics.Autonometer` or
            :func:`autonometrics.measure`.

        Examples
        --------
        >>> import autonometrics as anm
        >>> sys = anm.PromisedCycle.simple()
        >>> profile = anm.measure(sys)  # doctest: +SKIP
        >>> profile.coherence  # doctest: +SKIP
        0.92...
        """
        return cls(
            length=length,
            period=4,
            alphabet=4,
            p_noise=p_noise,
            seed=seed,
        )

    def _build(self) -> None:
        rng = np.random.default_rng(self._seed)
        idx = np.arange(self._length, dtype=np.int64) % self._period
        base_declared = idx.astype(np.int64)

        if self._p_env > 0.0:
            env_mask = rng.random(self._length) < self._p_env
            env_alts = rng.integers(0, self._alphabet, size=self._length).astype(
                np.int64
            )
            declared = np.where(env_mask, env_alts, base_declared).astype(np.int64)
        else:
            declared = base_declared

        if self._mode == _MODE_ADVERSARIAL:
            executed = ((declared + 1) % self._alphabet).astype(np.int64)
        else:
            mask = rng.random(self._length) < self._p_noise
            random_alts = rng.integers(0, self._alphabet, size=self._length).astype(
                np.int64
            )
            executed = np.where(mask, random_alts, declared).astype(np.int64)

        self._declared = declared
        self._executed = executed

    def _ensure_built(self) -> None:
        if self._declared is None or self._executed is None:
            self._build()

    def get_state_history(self) -> np.ndarray:
        """Return the executed trajectory (the system's observable behaviour)."""
        self._ensure_built()
        assert self._executed is not None
        return self._executed.copy()

    def get_env_history(self) -> np.ndarray:
        """Return a constant placeholder environment.

        ``PromisedCycle`` has no exogenous environment; the constant
        zero array is used for protocol symmetry with adapters that
        do. Closure-style metrics will see a non-informative ``env``
        and behave accordingly.
        """
        self._ensure_built()
        return np.zeros(self._length, dtype=np.int64)

    def get_declared_executed(self) -> tuple[np.ndarray, np.ndarray]:
        """Return ``(declared, executed)`` parallel trajectories for CBA."""
        self._ensure_built()
        assert self._declared is not None
        assert self._executed is not None
        return self._declared.copy(), self._executed.copy()

    def replay_from_perturbation(
        self,
        t_star: int,
        n_steps: int,
        rng: np.random.Generator | None = None,
    ) -> np.ndarray:
        """Return the post-perturbation focal slice for the persistence axis.

        ``PromisedCycle`` generates its executed trajectory from the
        time index alone (the next executed symbol does not depend on
        the current one — it depends on ``t mod period`` and, in
        ``random_noise`` mode, an independent noise draw cached at
        construction time). A single-element perturbation of the
        state at ``t_star`` therefore has **no effect** on the
        subsequent executed trajectory, and the post-perturbation
        slice equals the unperturbed slice.

        This is a structural property of the adapter, not a bug:
        ``PromisedCycle`` is by design **insensitive to state
        perturbations**, so the persistence axis returns its upper
        boundary on this substrate. Reporting that boundary value is
        the honest behaviour; faking a non-trivial perturbation
        response would launder the metric.
        """
        del rng
        self._ensure_built()
        assert self._executed is not None
        if t_star < 0 or t_star >= self._length - 1:
            raise ValueError(
                f"t_star must be in [0, {self._length - 2}]; got {t_star}"
            )
        if n_steps < 1:
            raise ValueError(f"n_steps must be positive; got {n_steps}")
        if t_star + n_steps >= self._length:
            raise ValueError(
                f"t_star + n_steps must be < {self._length}; "
                f"got {t_star + n_steps}"
            )
        return self._executed[t_star + 1 : t_star + 1 + n_steps].copy()

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def p_noise(self) -> float:
        return self._p_noise

    @property
    def p_env(self) -> float:
        return self._p_env

    @property
    def alphabet(self) -> int:
        return self._alphabet

    @property
    def period(self) -> int:
        return self._period

    @property
    def length(self) -> int:
        return self._length
