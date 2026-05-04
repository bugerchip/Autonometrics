"""Autonometrics: instrument for quantifying structural self-determination.

This package provides tools to measure the degree to which a system's
behaviour is determined by its own internally generated constraints
versus externally imposed ones, using formalisations drawn from
information theory, self-determination theory, and related traditions.

Status: alpha, API unstable.
"""

from autonometrics.adapters import CSVTrajectory, PromisedCycle, SimpleAutomaton
from autonometrics.core import (
    ALL_AXES,
    AXES,
    SUPPORTED_METRICS,
    Autonometer,
    AutonomySystem,
    measure,
)
from autonometrics.metrics import (
    compute_albantakis,
    compute_cba_theil_u,
    compute_constraint_closure,
    compute_memory_endo_ratio,
    compute_rai_proxy_persistence,
)
from autonometrics.profile import AutonomyProfile

# Canonical aliases for the metric-computing functions. These mirror
# the canonical axis names exposed in :data:`AXES` and the README. The
# original ``compute_*`` functions are kept untouched for backward
# compatibility; the aliases below are the recommended entry points.
compute_closure = compute_albantakis
compute_constraint = compute_constraint_closure
compute_persistence = compute_rai_proxy_persistence
compute_coherence = compute_cba_theil_u
# ``compute_memory`` already matches its canonical name, but we expose
# a same-named alias for symmetry with the rest of the canonical set.
compute_memory = compute_memory_endo_ratio

__version__ = "0.8.2a0"

__all__ = [
    "ALL_AXES",
    "AXES",
    "Autonometer",
    "AutonomyProfile",
    "AutonomySystem",
    "CSVTrajectory",
    "PromisedCycle",
    "SUPPORTED_METRICS",
    "SimpleAutomaton",
    "__version__",
    # Canonical compute_* aliases (recommended).
    "compute_closure",
    "compute_coherence",
    "compute_constraint",
    "compute_memory",
    "compute_persistence",
    # Internal compute_* names (kept for backward compatibility).
    "compute_albantakis",
    "compute_cba_theil_u",
    "compute_constraint_closure",
    "compute_memory_endo_ratio",
    "compute_rai_proxy_persistence",
    # Top-level convenience.
    "measure",
]
