"""Elementary cellular automaton (ECA) wrapped as an :class:`AutonomySystem`.

ECAs are 1D binary cellular automata indexed by an 8-bit ``rule`` number,
following the convention of Wolfram (1983). Each cell at the next
timestep is determined by the triple ``(left, centre, right)`` of the
previous step through a lookup table encoded in the rule number's bits.

The protocol exposed here is the natural temporal projection of the
2D grid onto a single focal cell:

- ``state[t]`` is the binary value of the focal (centre) cell at
  timestep ``t``.
- ``env[t]`` is the pair ``(left[t], right[t])`` of the cell's two
  immediate neighbours, encoded as an integer in ``{0, 1, 2, 3}``.

The focal cell does not control its neighbours' values, so reading the
neighbours as the environment respects the causal asymmetry the closure
metric needs.

References
----------
- Wolfram, S. (1983). *Statistical mechanics of cellular automata*.
  Reviews of Modern Physics 55(3).
- Wolfram, S. (2002). *A New Kind of Science*. Wolfram Media.
"""

from __future__ import annotations

import numpy as np

_INIT_RANDOM = "random"
_INIT_SINGLE = "single"
_VALID_INITS = frozenset({_INIT_RANDOM, _INIT_SINGLE})


class ECASystem:
    """Wolfram-style elementary cellular automaton as an :class:`AutonomySystem`."""

    def __init__(
        self,
        rule: int,
        n_steps: int,
        width: int = 101,
        seed: int = 0,
        init: str = _INIT_RANDOM,
    ) -> None:
        if not 0 <= rule <= 255:
            raise ValueError(f"rule must be in [0, 255], got {rule}")
        if n_steps < 2:
            raise ValueError(f"n_steps must be at least 2, got {n_steps}")
        if width < 5:
            raise ValueError(f"width must be at least 5, got {width}")
        if init not in _VALID_INITS:
            raise ValueError(f"init must be one of {sorted(_VALID_INITS)}, got {init!r}")

        self._rule = int(rule)
        self._n_steps = int(n_steps)
        self._width = int(width)
        self._seed = int(seed)
        self._init = init
        self._rng = np.random.default_rng(seed)

        self._state_history: np.ndarray | None = None
        self._env_history: np.ndarray | None = None

    def _initial_row(self) -> np.ndarray:
        if self._init == _INIT_SINGLE:
            row = np.zeros(self._width, dtype=np.int64)
            row[self._width // 2] = 1
            return row
        return self._rng.integers(0, 2, size=self._width).astype(np.int64)

    def _step(self, row: np.ndarray) -> np.ndarray:
        left = np.roll(row, 1)
        right = np.roll(row, -1)
        pattern = (left << 2) | (row << 1) | right
        return ((self._rule >> pattern) & 1).astype(np.int64)

    def run(self) -> None:
        """Evolve the grid and cache the focal-cell state and neighbour env."""
        centre = self._width // 2
        row = self._initial_row()

        states = np.empty(self._n_steps, dtype=np.int64)
        envs = np.empty(self._n_steps, dtype=np.int64)

        for t in range(self._n_steps):
            states[t] = int(row[centre])
            envs[t] = int(row[centre - 1] * 2 + row[(centre + 1) % self._width])
            row = self._step(row)

        self._state_history = states
        self._env_history = envs

    def get_state_history(self) -> np.ndarray:
        if self._state_history is None:
            self.run()
        assert self._state_history is not None
        return self._state_history.copy()

    def get_env_history(self) -> np.ndarray:
        if self._env_history is None:
            self.run()
        assert self._env_history is not None
        return self._env_history.copy()

    def get_causal_graph(self) -> np.ndarray:
        """Return the causal-dependency graph among the system's cells.

        The system has one constraint per cell on the periodic
        ring of length ``width``. Each cell at position ``p``
        reads cells ``(p - 1) % width``, ``p`` and
        ``(p + 1) % width`` in the previous timestep, so the
        returned matrix has, for each row ``p``, exactly three
        ``True`` entries (one of which is ``[p, p]`` itself, the
        self-loop). The boundary is periodic.
        """
        n = self._width
        graph = np.zeros((n, n), dtype=bool)
        for p in range(n):
            graph[p, (p - 1) % n] = True
            graph[p, p] = True
            graph[p, (p + 1) % n] = True
        return graph

    @property
    def rule(self) -> int:
        return self._rule
