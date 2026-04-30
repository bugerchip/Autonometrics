"""Adapters that wrap concrete system implementations behind the ``AutonomySystem`` protocol."""

from autonometrics.adapters.automaton import SimpleAutomaton
from autonometrics.adapters.csv_trajectory import CSVTrajectory

__all__ = ["CSVTrajectory", "SimpleAutomaton"]
