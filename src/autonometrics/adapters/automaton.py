"""Simple discrete-state automaton used to demonstrate autonomy measurements.

Two factory constructors produce qualitatively different systems:

- ``from_self_generated_rules`` builds an automaton whose transitions
  depend only on its own previous state — the environment is observed
  but ignored. Its autonomy score should be close to ``1``.
- ``from_external_rules`` builds an automaton whose transitions are
  driven by the environment input, with a small amount of hidden
  noise so that ``H(S_{t+1} | E_t)`` remains positive (a necessary
  condition for the Albantakis-style normalisation). Its autonomy
  score should be close to ``0``.

This class is intentionally minimal; it exists to make the
cross-substrate measurement story tangible in a ``hello world`` demo.
"""

from __future__ import annotations

import numpy as np

_MODE_SELF = "self_generated"
_MODE_EXTERNAL = "external"


class SimpleAutomaton:
    """Discrete-state automaton with self-generated or externally imposed rules."""

    def __init__(
        self,
        *,
        mode: str,
        n_states: int,
        env: np.ndarray,
        seed: int = 0,
        external_noise: float = 0.15,
    ) -> None:
        if mode not in (_MODE_SELF, _MODE_EXTERNAL):
            raise ValueError(f"Unknown mode {mode!r}")
        if n_states < 2:
            raise ValueError("n_states must be at least 2")
        if not 0.0 <= external_noise < 1.0:
            raise ValueError("external_noise must lie in [0.0, 1.0)")

        env_arr = np.asarray(env).ravel().astype(np.int64, copy=False)
        if env_arr.size < 2:
            raise ValueError("env must contain at least 2 timesteps")

        self._mode = mode
        self._n_states = n_states
        self._env = env_arr
        self._seed = int(seed)
        self._external_noise = float(external_noise)
        self._rng = np.random.default_rng(seed)

        if mode == _MODE_SELF:
            self._self_transition = self._build_self_transition(n_states)
            self._env_transition: np.ndarray | None = None
        else:
            env_alphabet_size = int(env_arr.max()) + 1
            self._env_transition = self._rng.integers(0, n_states, size=env_alphabet_size).astype(
                np.int64
            )
            self._self_transition = None

        self._state_history: np.ndarray | None = None
        self._noise_plan: np.ndarray | None = None
        self._noise_values: np.ndarray | None = None

    def _build_self_transition(self, n_states: int) -> np.ndarray:
        """Build a single-cycle permutation, guaranteeing no fixed points."""
        order = self._rng.permutation(n_states)
        table = np.empty(n_states, dtype=np.int64)
        for i in range(n_states):
            table[order[i]] = order[(i + 1) % n_states]
        return table

    @classmethod
    def from_self_generated_rules(
        cls,
        n_states: int,
        env: np.ndarray,
        seed: int = 0,
    ) -> SimpleAutomaton:
        """Build an automaton whose transitions depend only on its own state."""
        return cls(mode=_MODE_SELF, n_states=n_states, env=env, seed=seed)

    @classmethod
    def from_external_rules(
        cls,
        n_states: int,
        env: np.ndarray,
        seed: int = 0,
        noise: float = 0.15,
    ) -> SimpleAutomaton:
        """Build an automaton whose transitions are driven by the environment.

        ``noise`` is the probability that a given transition is resolved
        by a hidden random draw instead of the environment table. A
        small positive value is required so the metric's denominator,
        ``H(S_{t+1} | E_t)``, remains strictly positive.
        """
        return cls(
            mode=_MODE_EXTERNAL,
            n_states=n_states,
            env=env,
            seed=seed,
            external_noise=noise,
        )

    def run(self) -> None:
        """Execute the automaton over the full environment history and cache states.

        For external mode, the per-step noise plan is also cached
        (mask + replacement values) so that ``replay_from_perturbation``
        can reuse the exact same noise stream and isolate the effect of
        the injected perturbation.
        """
        n = self._env.size
        history = np.empty(n, dtype=np.int64)
        history[0] = 0

        if self._mode == _MODE_SELF:
            assert self._self_transition is not None
            table = self._self_transition
            for i in range(1, n):
                history[i] = int(table[history[i - 1]])
            self._noise_plan = None
            self._noise_values = None
        else:
            assert self._env_transition is not None
            table = self._env_transition
            noise = self._external_noise
            plan = np.zeros(n, dtype=bool)
            values = np.zeros(n, dtype=np.int64)
            for i in range(1, n):
                if self._rng.random() < noise:
                    drawn = int(self._rng.integers(0, self._n_states))
                    history[i] = drawn
                    plan[i] = True
                    values[i] = drawn
                else:
                    history[i] = int(table[int(self._env[i - 1])])
            self._noise_plan = plan
            self._noise_values = values

        self._state_history = history

    def get_state_history(self) -> np.ndarray:
        if self._state_history is None:
            self.run()
        assert self._state_history is not None
        return self._state_history.copy()

    def get_env_history(self) -> np.ndarray:
        return self._env.copy()

    def replay_from_perturbation(
        self,
        t_star: int,
        n_steps: int,
        rng: np.random.Generator | None = None,
    ) -> np.ndarray:
        """Return the focal trajectory after advancing the state at ``t_star``.

        For ``self_generated`` mode the perturbed value is the next
        symbol in the state-cycle permutation; for ``external`` mode
        it is ``(state + 1) % n_states``. Subsequent steps reuse the
        original cached noise plan when present, so that the perturbed
        and the unperturbed trajectories differ only because of the
        injected perturbation. ``rng`` is accepted for protocol
        symmetry and is unused.
        """
        del rng
        if self._state_history is None:
            self.run()
        assert self._state_history is not None

        n = self._env.size
        if t_star < 0 or t_star >= n - 1:
            raise ValueError(f"t_star must be in [0, {n - 2}], got {t_star}")
        if n_steps < 1:
            raise ValueError(f"n_steps must be positive, got {n_steps}")
        if t_star + n_steps >= n:
            raise ValueError(
                f"t_star + n_steps must be < {n}, got {t_star + n_steps}"
            )

        baseline = int(self._state_history[t_star])
        perturbed = (baseline + 1) % self._n_states
        if perturbed == baseline:
            perturbed = (baseline + 1) % self._n_states

        out = np.empty(n_steps, dtype=np.int64)
        cur = perturbed

        if self._mode == _MODE_SELF:
            assert self._self_transition is not None
            table = self._self_transition
            for k in range(n_steps):
                cur = int(table[cur])
                out[k] = cur
        else:
            assert self._env_transition is not None
            assert self._noise_plan is not None
            assert self._noise_values is not None
            table = self._env_transition
            for k in range(n_steps):
                idx = t_star + 1 + k
                if self._noise_plan[idx]:
                    cur = int(self._noise_values[idx])
                else:
                    cur = int(table[int(self._env[idx - 1])])
                out[k] = cur
        return out

    def get_causal_graph(self) -> np.ndarray:
        """Return the single-node causal graph for this automaton.

        ``SimpleAutomaton`` always exposes one constraint: the
        update function of its single state variable. Whether the
        update reads its own previous value (``self_generated``)
        or the environment plus a hidden draw (``external``), the
        intra-system dependency graph is ``1 x 1``. In the
        self-generated mode the diagonal carries a self-loop; in
        the external mode it does not. Either way the node is
        alone, so under the package's constraint-closure
        operationalisation (cycles of length 2 or 3 only) the
        score is ``0.0``.
        """
        loops = self._mode == _MODE_SELF
        return np.array([[loops]], dtype=bool)

    @property
    def mode(self) -> str:
        return self._mode
