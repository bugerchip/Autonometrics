"""Core orchestrator for autonomy measurements."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np

from autonometrics.metrics import compute_albantakis
from autonometrics.profile import AutonomyProfile

SUPPORTED_METRICS: frozenset[str] = frozenset({"albantakis"})


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
    """Orchestrator that applies a metric to a system and returns a profile.

    Parameters
    ----------
    metric:
        Identifier of the metric to use. Currently only ``"albantakis"``
        is accepted. Additional metrics (Gershenson autopoietic ratio,
        SDT Relative Autonomy Index, Coherence-Based Alignment) will be
        registered here.
    """

    def __init__(self, metric: str = "albantakis") -> None:
        if metric not in SUPPORTED_METRICS:
            raise ValueError(f"Unknown metric {metric!r}. Supported: {sorted(SUPPORTED_METRICS)}")
        self.metric = metric

    def measure(self, system: AutonomySystem) -> AutonomyProfile:
        """Compute the autonomy profile of ``system``.

        The system must implement the :class:`AutonomySystem` protocol.
        """
        if not hasattr(system, "get_state_history") or not hasattr(system, "get_env_history"):
            raise TypeError(
                "system must implement the AutonomySystem protocol "
                "(get_state_history, get_env_history)"
            )

        states = np.asarray(system.get_state_history())
        env = np.asarray(system.get_env_history())

        if self.metric == "albantakis":
            score = compute_albantakis(states, env)
            return AutonomyProfile(
                ratio_endo_total=score,
                metadata={
                    "metric": "albantakis",
                    "n_timesteps": int(states.size),
                    "adapter": type(system).__name__,
                },
            )

        raise NotImplementedError(f"metric {self.metric!r} is not wired yet")
