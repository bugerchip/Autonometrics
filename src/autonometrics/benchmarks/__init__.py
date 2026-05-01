"""Reference systems with known autonomy structure for benchmarking.

These adapters expose canonical models from the cellular-automata and
Boolean-network literatures, plus simple period-``p`` controls, behind
the same :class:`autonometrics.AutonomySystem` protocol the rest of
the package uses. They exist so that the closure and memory axes can
be evaluated against systems whose autonomy properties are
independently understood, rather than against bespoke synthetic
adapters alone.

The benchmarks module is intentionally numpy-only and adds no new
runtime dependencies; it ships inside the installable package so that
``pip install autonometrics`` is enough to reproduce any benchmark
figure shipped with a release.
"""

from autonometrics.benchmarks.boolean_network import KauffmanNetwork
from autonometrics.benchmarks.canonical import PeriodicCycle
from autonometrics.benchmarks.eca import ECASystem

__all__ = ["ECASystem", "KauffmanNetwork", "PeriodicCycle"]
