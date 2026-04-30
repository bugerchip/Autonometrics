"""Core orchestrator for autonomy measurements."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, runtime_checkable

import numpy as np

from autonometrics.metrics import compute_albantakis, compute_autopoietic_ratio
from autonometrics.profile import AutonomyProfile

_MetricFn = Callable[[np.ndarray, np.ndarray], float]

_METRIC_REGISTRY: dict[str, _MetricFn] = {
    "albantakis": compute_albantakis,
    "autopoietic": compute_autopoietic_ratio,
}

_PROFILE_FIELD: dict[str, str] = {
    "albantakis": "ratio_endo_total",
    "autopoietic": "autopoietic_ratio",
}

SUPPORTED_METRICS: frozenset[str] = frozenset(_METRIC_REGISTRY)


@runtime_checkable
class AutonomySystem(Protocol):
    """Minimal interface a system must expose to be measured.

    Any object implementing ``get_state_history`` and
    ``get_env_history`` (both returning 1D integer ``np.ndarray``) can
    be passed to :meth:`Autonometer.measure`.
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

        field_values: dict[str, float] = {}
        for name in self.metrics:
            fn = _METRIC_REGISTRY[name]
            score = fn(states, env)
            field_values[_PROFILE_FIELD[name]] = score

        metadata = {
            "metrics": list(self.metrics),
            "metric": self.metrics[0],
            "n_timesteps": int(states.size),
            "adapter": type(system).__name__,
        }

        return AutonomyProfile(
            ratio_endo_total=field_values.get("ratio_endo_total"),
            autopoietic_ratio=field_values.get("autopoietic_ratio"),
            metadata=metadata,
        )
