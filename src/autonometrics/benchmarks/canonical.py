"""Canonical control systems for the benchmark suite.

Small, deterministic systems with closed-form expectations on the
``(closure, memory)`` plane. They serve as anchors: if a metric
disagrees with the closed-form expectation here, the metric, not the
benchmark, is suspect.
"""

from __future__ import annotations

import numpy as np


class PeriodicCycle:
    """Deterministic period-``p`` cycle with an i.i.d. environment.

    The state trajectory is ``state[t] = t mod period``; the environment
    is sampled uniformly at random from ``{0, ..., env_alphabet - 1}``
    and is independent of the state. This is the canonical "high
    closure, low joint memory contribution from environment" anchor:
    closure should approach ``1`` because the next state is fully
    determined by the previous one, and the memory ratio should sit
    near ``1`` because the environment carries (almost) no structural
    memory.
    """

    def __init__(
        self,
        period: int = 4,
        n_steps: int = 2000,
        env_alphabet: int = 3,
        seed: int = 0,
    ) -> None:
        if period < 2:
            raise ValueError(f"period must be at least 2, got {period}")
        if n_steps < 2:
            raise ValueError(f"n_steps must be at least 2, got {n_steps}")
        if env_alphabet < 2:
            raise ValueError(f"env_alphabet must be at least 2, got {env_alphabet}")

        self._period = int(period)
        self._n_steps = int(n_steps)
        self._env_alphabet = int(env_alphabet)
        self._seed = int(seed)
        self._rng = np.random.default_rng(seed)

        self._state_history = (np.arange(n_steps) % period).astype(np.int64)
        self._env_history = self._rng.integers(0, env_alphabet, size=n_steps).astype(np.int64)

    def get_state_history(self) -> np.ndarray:
        return self._state_history.copy()

    def get_env_history(self) -> np.ndarray:
        return self._env_history.copy()

    def get_causal_graph(self) -> np.ndarray:
        """Return the single-node causal graph: one self-loop, no cycles.

        The cycle has one constraint (the increment-and-modulo
        rule), which depends on its own previous state. The
        graph is therefore the ``1 x 1`` matrix ``[[True]]``: a
        self-loop. Under the package's constraint-closure
        operationalisation self-loops do not count as closure
        (only cycles of length 2 or 3 do), so this adapter
        scores ``0.0`` on ``constraint_closure``, exactly as the
        Montévil & Mossio framework predicts for a system
        composed of a single constraint.
        """
        return np.array([[True]], dtype=bool)

    @property
    def period(self) -> int:
        return self._period
