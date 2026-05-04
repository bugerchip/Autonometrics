"""Core orchestrator for autonomy measurements."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable

import numpy as np

from autonometrics.metrics import (
    compute_albantakis,
    compute_cba_theil_u,
    compute_constraint_closure,
    compute_memory_endo_ratio,
    compute_rai_proxy_persistence,
)
from autonometrics.profile import AutonomyProfile

_TrajectoryMetricFn = Callable[[np.ndarray, np.ndarray], float]
_GraphMetricFn = Callable[[np.ndarray], float]
_MetricFn = Callable[..., float]

_INPUT_TRAJECTORY = "states_env"
_INPUT_GRAPH = "causal_graph"
_INPUT_REPLAY = "states_env_replay"
_INPUT_DECLARED_EXECUTED = "declared_executed"

_METRIC_REGISTRY: dict[str, _MetricFn] = {
    "albantakis": compute_albantakis,
    "memory": compute_memory_endo_ratio,
    "constraint_closure": compute_constraint_closure,
    "persistence": compute_rai_proxy_persistence,
    "coherence": compute_cba_theil_u,
}

_METRIC_INPUT: dict[str, str] = {
    "albantakis": _INPUT_TRAJECTORY,
    "memory": _INPUT_TRAJECTORY,
    "constraint_closure": _INPUT_GRAPH,
    "persistence": _INPUT_REPLAY,
    "coherence": _INPUT_DECLARED_EXECUTED,
}

_PROFILE_FIELD: dict[str, str] = {
    "albantakis": "ratio_endo_total",
    "memory": "memory_endo_ratio",
    "constraint_closure": "constraint_closure",
    "persistence": "rai_proxy_persistence",
    "coherence": "cba_theil_u",
}

SUPPORTED_METRICS: frozenset[str] = frozenset(_METRIC_REGISTRY)


@runtime_checkable
class AutonomySystem(Protocol):
    """Minimal interface a system must expose to be measured.

    Any object implementing ``get_state_history`` and
    ``get_env_history`` (both returning 1D integer ``np.ndarray``) can
    be passed to :meth:`Autonometer.measure`.

    Adapters that want to be eligible for graph-based metrics (e.g.
    ``constraint_closure``) additionally expose ``get_causal_graph``
    returning a square ``(n, n)`` boolean adjacency matrix where
    entry ``[i, j]`` is ``True`` iff "constraint ``i`` depends on
    constraint ``j``". Adapters that cannot expose such a graph are
    free to omit the method or to raise ``NotImplementedError``;
    the orchestrator records ``None`` for the corresponding metric
    field rather than aborting the whole measurement.

    Adapters that want to be eligible for replay-based metrics (e.g.
    ``persistence``) additionally expose
    ``replay_from_perturbation(t_star, n_steps, rng=None)`` returning
    a 1-D integer ``np.ndarray`` of length ``n_steps`` containing the
    focal trajectory at times ``t_star + 1, ..., t_star + n_steps``
    after a single-element perturbation has been applied to the
    system's full internal state at time ``t_star``. Adapters that
    cannot replay (e.g. CSV-only trajectories) omit the method and
    the orchestrator records ``None`` for the corresponding metric
    field. The same fail-loudly contract used for ``get_causal_graph``
    applies here.

    Adapters that want to be eligible for the coherence axis (CBA)
    additionally expose ``get_declared_executed()`` returning a
    tuple ``(declared, executed)`` of 1-D integer ``np.ndarray`` of
    the same length, where ``declared`` is the system's *announced*
    trajectory (plan, prediction, declared intention) and
    ``executed`` is the *actually realised* trajectory. Adapters
    that have no declarative layer (e.g. cellular automata, Boolean
    networks, periodic cycles, ``SimpleAutomaton``) must not expose
    the method, or may return ``None``; the orchestrator records
    ``None`` for the corresponding metric field in those cases. The
    CBA axis is by design the narrowest in the atlas — only systems
    with a meaningful declarative layer are scored.
    """

    def get_state_history(self) -> np.ndarray: ...
    def get_env_history(self) -> np.ndarray: ...


class Autonometer:
    """Orchestrator that applies one or more metrics to a system.

    Parameters
    ----------
    metric:
        Single-metric convenience argument, kept for backward
        compatibility with ``v0.1.x``. Ignored when ``metrics`` is
        provided.
    metrics:
        Preferred argument. A list of metric identifiers; each entry
        must be in :data:`SUPPORTED_METRICS`. Defaults to
        ``["albantakis"]`` when neither ``metric`` nor ``metrics`` is
        given.
    """

    def __init__(
        self,
        metric: str | None = None,
        metrics: list[str] | None = None,
    ) -> None:
        if metrics is not None:
            resolved = list(metrics)
        elif metric is not None:
            resolved = [metric]
        else:
            resolved = ["albantakis"]

        if not resolved:
            raise ValueError("metrics must contain at least one metric identifier")

        for name in resolved:
            if name not in _METRIC_REGISTRY:
                raise ValueError(f"Unknown metric {name!r}. Supported: {sorted(_METRIC_REGISTRY)}")

        self.metrics: list[str] = resolved

    @property
    def metric(self) -> str:
        """First metric in :attr:`metrics`; kept for backward compatibility."""
        return self.metrics[0]

    def measure(self, system: AutonomySystem) -> AutonomyProfile:
        """Compute the autonomy profile of ``system``.

        The system must implement the :class:`AutonomySystem` protocol.
        Every metric registered for this instance is evaluated and its
        result written to the matching field of :class:`AutonomyProfile`.
        Fields corresponding to metrics that were not requested stay
        ``None``.
        """
        if not hasattr(system, "get_state_history") or not hasattr(system, "get_env_history"):
            raise TypeError(
                "system must implement the AutonomySystem protocol "
                "(get_state_history, get_env_history)"
            )

        states = np.asarray(system.get_state_history())
        env = np.asarray(system.get_env_history())

        field_values: dict[str, float | None] = {}
        for name in self.metrics:
            field_values[_PROFILE_FIELD[name]] = self._score(name, system, states, env)

        metadata: dict[str, Any] = {
            "metrics": list(self.metrics),
            "metric": self.metrics[0],
            "n_timesteps": int(states.size),
            "adapter": type(system).__name__,
        }

        return AutonomyProfile(
            ratio_endo_total=field_values.get("ratio_endo_total"),
            memory_endo_ratio=field_values.get("memory_endo_ratio"),
            constraint_closure=field_values.get("constraint_closure"),
            rai_proxy_persistence=field_values.get("rai_proxy_persistence"),
            cba_theil_u=field_values.get("cba_theil_u"),
            metadata=metadata,
        )

    @staticmethod
    def _score(
        name: str,
        system: AutonomySystem,
        states: np.ndarray,
        env: np.ndarray,
    ) -> float | None:
        """Dispatch ``name`` to its registered metric with the right inputs."""
        fn = _METRIC_REGISTRY[name]
        kind = _METRIC_INPUT[name]
        if kind == _INPUT_TRAJECTORY:
            return float(fn(states, env))
        if kind == _INPUT_GRAPH:
            graph_fn = getattr(system, "get_causal_graph", None)
            if graph_fn is None:
                return None
            try:
                graph = graph_fn()
            except NotImplementedError:
                return None
            return float(fn(np.asarray(graph)))
        if kind == _INPUT_REPLAY:
            replay_fn = getattr(system, "replay_from_perturbation", None)
            if replay_fn is None:
                return None
            try:
                return float(fn(states, env, replay_fn))
            except NotImplementedError:
                return None
        if kind == _INPUT_DECLARED_EXECUTED:
            de_fn = getattr(system, "get_declared_executed", None)
            if de_fn is None:
                return None
            try:
                pair = de_fn()
            except NotImplementedError:
                return None
            if pair is None:
                return None
            declared, executed = pair
            return float(fn(np.asarray(declared), np.asarray(executed)))
        raise RuntimeError(f"Unknown metric input kind for {name!r}: {kind!r}")
