"""Random Boolean network (Kauffman NK) wrapped as an :class:`AutonomySystem`.

Each of the ``n_nodes`` binary nodes has ``k`` inputs drawn from the
network and an independently sampled boolean truth table over its
``2 ** k`` input patterns. The network evolves synchronously.

A single focal node carries the system trajectory and a separate,
non-overlapping node carries the environment trajectory, so the
focal node's structural self-determination is read against a node it
does not control.

The ``coupling`` parameter shapes the focal node's wiring:

- ``coupling = 0``: every one of the focal node's ``k`` inputs is the
  focal node itself, so its next state depends only on its own past.
  Closure tends to ``1`` by construction.
- ``coupling = 1``: none of the focal node's inputs is the focal
  node. Its next state is fully driven by other nodes.
- intermediate values mix self-loops with external inputs, sweeping
  the closure axis continuously.

References
----------
- Kauffman, S. A. (1969). *Metabolic stability and epigenesis in
  randomly constructed genetic nets*. Journal of Theoretical Biology
  22(3).
- Kauffman, S. A. (1993). *The Origins of Order*. Oxford University Press.
"""

from __future__ import annotations

import numpy as np


class KauffmanNetwork:
    """Synchronous Kauffman NK boolean network with tunable focal coupling."""

    def __init__(
        self,
        n_nodes: int = 10,
        k: int = 3,
        n_steps: int = 2000,
        coupling: float = 0.5,
        seed: int = 0,
    ) -> None:
        if n_nodes < 3:
            raise ValueError(f"n_nodes must be at least 3, got {n_nodes}")
        if k < 1:
            raise ValueError(f"k must be at least 1, got {k}")
        if k > n_nodes:
            raise ValueError(f"k ({k}) cannot exceed n_nodes ({n_nodes})")
        if n_steps < 2:
            raise ValueError(f"n_steps must be at least 2, got {n_steps}")
        if not 0.0 <= coupling <= 1.0:
            raise ValueError(f"coupling must lie in [0.0, 1.0], got {coupling}")

        self._n_nodes = int(n_nodes)
        self._k = int(k)
        self._n_steps = int(n_steps)
        self._coupling = float(coupling)
        self._seed = int(seed)
        self._rng = np.random.default_rng(seed)

        self._focal = 0
        self._env_node = self._choose_env_node()

        self._inputs = self._build_inputs()
        self._truth_tables = self._rng.integers(0, 2, size=(self._n_nodes, 1 << self._k)).astype(
            np.int64
        )

        self._state_history: np.ndarray | None = None
        self._env_history: np.ndarray | None = None
        self._full_state_history: np.ndarray | None = None
        self._weights = (1 << np.arange(self._k - 1, -1, -1)).astype(np.int64)

    def _choose_env_node(self) -> int:
        candidates = [i for i in range(self._n_nodes) if i != self._focal]
        return int(self._rng.choice(candidates))

    def _build_inputs(self) -> np.ndarray:
        """Return shape ``(n_nodes, k)`` matrix of input indices per node."""
        inputs = np.empty((self._n_nodes, self._k), dtype=np.int64)
        n_self = int(round(self._k * (1.0 - self._coupling)))
        n_self = min(max(n_self, 0), self._k)

        non_focal_pool = np.array(
            [i for i in range(self._n_nodes) if i != self._focal], dtype=np.int64
        )
        focal_external = self._rng.choice(non_focal_pool, size=self._k - n_self, replace=True)
        focal_self = np.full(n_self, self._focal, dtype=np.int64)
        focal_inputs = np.concatenate([focal_self, focal_external])
        self._rng.shuffle(focal_inputs)
        inputs[self._focal] = focal_inputs

        for node in range(self._n_nodes):
            if node == self._focal:
                continue
            inputs[node] = self._rng.integers(0, self._n_nodes, size=self._k).astype(np.int64)

        return inputs

    def _step_full(self, state: np.ndarray) -> np.ndarray:
        """Apply one synchronous update to the full network state."""
        indexed_inputs = state[self._inputs]
        patterns = indexed_inputs.dot(self._weights)
        return self._truth_tables[np.arange(self._n_nodes), patterns].astype(np.int64)

    def run(self) -> None:
        """Evolve the network and cache focal-state and env-node trajectories.

        The full network state is also cached as ``_full_state_history``
        to support replay-based metrics (perturbation persistence).
        """
        state = self._rng.integers(0, 2, size=self._n_nodes).astype(np.int64)

        states = np.empty(self._n_steps, dtype=np.int64)
        envs = np.empty(self._n_steps, dtype=np.int64)
        full = np.empty((self._n_steps, self._n_nodes), dtype=np.int64)

        for t in range(self._n_steps):
            full[t] = state
            states[t] = int(state[self._focal])
            envs[t] = int(state[self._env_node])
            state = self._step_full(state)

        self._state_history = states
        self._env_history = envs
        self._full_state_history = full

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

    def replay_from_perturbation(
        self,
        t_star: int,
        n_steps: int,
        rng: np.random.Generator | None = None,
    ) -> np.ndarray:
        """Return the focal trajectory after flipping the focal node at ``t_star``.

        The full network state at time ``t_star`` is taken from the
        cached evolution, the focal node's bit is flipped, and the
        synchronous update is applied for ``n_steps`` further steps.
        ``rng`` is accepted for protocol symmetry but unused: the
        Kauffman network is fully deterministic given the seeded
        truth tables and the (already-fixed) initial state.
        """
        del rng
        if self._full_state_history is None:
            self.run()
        assert self._full_state_history is not None

        if t_star < 0 or t_star >= self._n_steps - 1:
            raise ValueError(f"t_star must be in [0, {self._n_steps - 2}], got {t_star}")
        if n_steps < 1:
            raise ValueError(f"n_steps must be positive, got {n_steps}")
        if t_star + n_steps >= self._n_steps:
            raise ValueError(f"t_star + n_steps must be < {self._n_steps}, got {t_star + n_steps}")

        state = self._full_state_history[t_star].copy()
        state[self._focal] = 1 - int(state[self._focal])

        out = np.empty(n_steps, dtype=np.int64)
        for k in range(n_steps):
            state = self._step_full(state)
            out[k] = int(state[self._focal])
        return out

    def get_causal_graph(self) -> np.ndarray:
        """Return the causal-dependency graph among the network's nodes.

        The network has one constraint per node. Node ``i``'s
        update function reads the nodes listed in
        ``self._inputs[i]``, so the returned matrix has, for each
        row ``i``, ``True`` at the unique input columns. Repeated
        inputs (which can occur for the focal node when
        ``coupling`` produces multiple self-references) are
        deduplicated by the boolean encoding.
        """
        n = self._n_nodes
        graph = np.zeros((n, n), dtype=bool)
        for node in range(n):
            for src in self._inputs[node]:
                graph[node, int(src)] = True
        return graph

    @property
    def coupling(self) -> float:
        return self._coupling
