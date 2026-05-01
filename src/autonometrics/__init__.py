"""Autonometrics: instrument for quantifying structural self-determination.

This package provides tools to measure the degree to which a system's
behaviour is determined by its own internally generated constraints
versus externally imposed ones, using formalisations drawn from
information theory, self-determination theory, and related traditions.

Status: alpha, API unstable.
"""

from autonometrics.adapters import CSVTrajectory, SimpleAutomaton
from autonometrics.core import Autonometer, AutonomySystem
from autonometrics.metrics import compute_albantakis, compute_memory_endo_ratio
from autonometrics.profile import AutonomyProfile

__version__ = "0.3.0a0"

__all__ = [
    "Autonometer",
    "AutonomyProfile",
    "AutonomySystem",
    "CSVTrajectory",
    "SimpleAutomaton",
    "__version__",
    "compute_albantakis",
    "compute_memory_endo_ratio",
]
