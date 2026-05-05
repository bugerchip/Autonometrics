"""Adapters that wrap concrete system implementations behind the ``AutonomySystem`` protocol."""

from autonometrics.adapters.automaton import SimpleAutomaton
from autonometrics.adapters.csv_trajectory import CSVTrajectory
from autonometrics.adapters.llm_transcript import LLMTranscriptAdapter
from autonometrics.adapters.promised_cycle import PromisedCycle

__all__ = ["CSVTrajectory", "LLMTranscriptAdapter", "PromisedCycle", "SimpleAutomaton"]
