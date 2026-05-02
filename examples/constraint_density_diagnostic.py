"""Constraint-closure diagnostic: how does the metric react to connection density?

Background
----------
The constraint-closure axis shipped in ``v0.6.0a0`` measures the
fraction of a system's update functions that lie on at least one
simple directed cycle of length 2 or 3 in the causal-dependency
graph. Two regions of the graph space drive the score to its
boundary values **by construction**, independently of any
empirical content:

- **Single-constraint trivial-zero theorem.** If the system has
  exactly ``n = 1`` update function, no simple cycle of length
  ``>= 2`` can exist (such a cycle requires at least two distinct
  nodes). The metric therefore returns ``0.0`` for any
  one-constraint system, regardless of whether the lone update
  function reads its own previous value (``self_generated``
  modes) or anything else. The score is a fact about the
  cardinality of the constraint set, not about its dynamics.

- **Symmetric-neighbour saturation theorem.** If every node's
  update function reads at least one node that reads it back,
  every node sits on a length-2 cycle and the metric returns
  ``1.0``. The canonical case is an elementary cellular
  automaton on a periodic ring: cell ``p`` reads cells
  ``p - 1, p, p + 1`` and is in turn read by cells ``p - 1`` and
  ``p + 1``, so each cell saturates the metric purely from the
  ring topology. This region is reached by any sufficiently
  dense-and-symmetric dependency graph.

Both regions are mathematically forced. They are the
constraint-closure analogue of the closure-saturation theorem
documented in ``v0.5.1a0`` for the Albantakis closure axis. The
present script verifies their joint shape empirically by sweeping
**connection density** in a controllable system and showing that
constraint-closure walks smoothly from the lower boundary to the
upper one as density grows.

Method
------
For each value ``K`` in a sweep (default ``1, 2, ..., n_nodes - 1``)
the diagnostic generates ``n_seeds`` independent Kauffman networks
with ``n_nodes`` binary nodes and ``K`` random inputs per node. The
input rows of the resulting causal graph are deduplicated when
read by ``compute_constraint_closure``, so ``K`` acts as the
upper bound on the in-degree per node and therefore controls the
expected number of mutually-connected pairs.

Per ``K`` we compute ``constraint_closure`` from
``KauffmanNetwork.get_causal_graph()`` directly, without running
the network's trajectory: the metric is purely topological and
does not need a state history. The aggregate report reduces the
seeds to ``mean +/- std`` per ``K``.

Outputs
-------
- A per-row table on stdout.
- A CSV at ``docs/benchmarks/constraint_density_v0.6.1.csv``
  (overridable via ``--output``).
- An aggregate summary table with ``mean +/- std`` of constraint
  per ``K``.
- A diagnosis line that flags whether the curve walks from
  ``constraint approx 0`` at low ``K`` to ``constraint approx 1``
  at high ``K`` monotonically, i.e. whether the two boundary
  theorems hold jointly on the swept zoo.

Usage
-----
::

    python examples/constraint_density_diagnostic.py
    python examples/constraint_density_diagnostic.py --quick
    python examples/constraint_density_diagnostic.py --n-nodes 12 --n-seeds 5

The script is numpy-only; rendering the optional curve figure
lives in ``examples/constraint_density_plot.py``.
"""

from __future__ import annotations

import argparse
import csv
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from autonometrics.benchmarks import KauffmanNetwork
from autonometrics.metrics import compute_constraint_closure

_DEFAULT_N_NODES = 10
_DEFAULT_N_STEPS = 2
_DEFAULT_N_SEEDS = 10
_QUICK_N_SEEDS = 3


def _default_k_values(n_nodes: int) -> tuple[int, ...]:
    """K from 1 to ``n_nodes - 1`` inclusive."""
    return tuple(range(1, n_nodes))


def _quick_k_values(n_nodes: int) -> tuple[int, ...]:
    """Coarse three-point sweep covering low / middle / high density."""
    return (1, max(1, n_nodes // 2), max(1, n_nodes - 1))


@dataclass
class ConstraintDensityPoint:
    """A single ``(K, seed) -> constraint_closure`` measurement."""

    n_nodes: int
    k: int
    seed: int
    constraint: float | None
    notes: str


def iter_configs(
    k_values: tuple[int, ...],
    n_seeds: int,
    n_nodes: int,
    n_steps: int,
) -> Iterator[tuple[int, int, int, KauffmanNetwork]]:
    """Yield ``(n_nodes, k, seed, system)`` tuples for the sweep."""
    for k in k_values:
        for seed in range(n_seeds):
            yield n_nodes, k, seed, KauffmanNetwork(
                n_nodes=n_nodes,
                k=k,
                n_steps=n_steps,
                coupling=1.0,
                seed=seed,
            )


def measure_one(system: KauffmanNetwork) -> tuple[float | None, str]:
    """Compute constraint_closure on ``system.get_causal_graph()``."""
    try:
        graph = system.get_causal_graph()
        return float(compute_constraint_closure(graph)), ""
    except ValueError as exc:
        cleaned = " ".join(str(exc).split())
        return None, cleaned[:80]


def run_sweep(
    n_nodes: int = _DEFAULT_N_NODES,
    k_values: tuple[int, ...] | None = None,
    n_seeds: int = _DEFAULT_N_SEEDS,
    n_steps: int = _DEFAULT_N_STEPS,
) -> list[ConstraintDensityPoint]:
    """Sweep ``k_values`` against ``n_seeds`` and collect points."""
    if k_values is None:
        k_values = _default_k_values(n_nodes)
    points: list[ConstraintDensityPoint] = []
    for n_n, k, seed, system in iter_configs(k_values, n_seeds, n_nodes, n_steps):
        score, notes = measure_one(system)
        points.append(
            ConstraintDensityPoint(
                n_nodes=n_n,
                k=k,
                seed=seed,
                constraint=score,
                notes=notes,
            )
        )
    return points


def print_table(points: list[ConstraintDensityPoint]) -> None:
    """Pretty-print one row per measurement."""
    fmt = "{:>4} {:>4} {:>4} {:>10} {}"
    print(fmt.format("n", "k", "seed", "constraint", "notes"))
    print(fmt.format("-" * 4, "-" * 4, "----", "-" * 10, "-" * 30))
    for p in points:
        c = "n/a" if p.constraint is None else f"{p.constraint:.4f}"
        print(fmt.format(p.n_nodes, p.k, p.seed, c, p.notes))


_CSV_FIELDS = ["n_nodes", "k", "seed", "constraint", "notes"]


def write_csv(points: list[ConstraintDensityPoint], path: Path) -> None:
    """Persist the points to ``path`` as a UTF-8 CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        for p in points:
            row = asdict(p)
            row["constraint"] = (
                "" if row["constraint"] is None else f"{row['constraint']:.6f}"
            )
            writer.writerow(row)


def aggregate(points: list[ConstraintDensityPoint]) -> dict[int, dict[str, Any]]:
    """Reduce per-seed measurements to mean / std per ``K``."""
    by_k: dict[int, list[ConstraintDensityPoint]] = {}
    for p in points:
        by_k.setdefault(p.k, []).append(p)

    out: dict[int, dict[str, Any]] = {}
    for k_value, group in sorted(by_k.items()):
        valid = [g for g in group if g.constraint is not None]
        if valid:
            scores = np.array([g.constraint for g in valid], dtype=float)
            out[k_value] = {
                "n_total": len(group),
                "n_valid": len(valid),
                "constraint_mean": float(np.mean(scores)),
                "constraint_std": float(np.std(scores)),
            }
        else:
            out[k_value] = {
                "n_total": len(group),
                "n_valid": 0,
                "constraint_mean": float("nan"),
                "constraint_std": float("nan"),
            }
    return out


def print_aggregate(stats: dict[int, dict[str, Any]]) -> None:
    """Pretty-print the per-K aggregate stats."""
    print()
    print("Aggregate (mean +/- std per K):")
    fmt = "{:>4} {:>5} {:>22}"
    print(fmt.format("k", "n", "constraint"))
    print(fmt.format("-" * 4, "-" * 5, "-" * 22))
    for k_value, row in stats.items():
        if row["n_valid"] == 0:
            c_str = "n/a"
        else:
            c_str = f"{row['constraint_mean']:.4f} +/- {row['constraint_std']:.4f}"
        print(fmt.format(k_value, f"{row['n_valid']}/{row['n_total']}", c_str))


def diagnosis_line(stats: dict[int, dict[str, Any]]) -> str:
    """Return a single-line verdict on whether the curve walks the boundary theorems."""
    k_values = sorted(stats.keys())
    means = [stats[k]["constraint_mean"] for k in k_values]
    valid = [
        (k, m) for k, m in zip(k_values, means, strict=True) if not np.isnan(m)
    ]
    if len(valid) < 2:
        return "[N/A] not enough valid K levels to assess the curve."

    first_k, first_c = valid[0]
    last_k, last_c = valid[-1]
    rise = last_c - first_c

    monotonic = all(
        valid[i][1] <= valid[i + 1][1] + 1e-3 for i in range(len(valid) - 1)
    )

    low_ok = first_c < 0.4
    high_ok = last_c > 0.7

    if rise > 0.5 and monotonic and low_ok and high_ok:
        return (
            f"[OK] constraint(K={first_k}) = {first_c:.3f} -> "
            f"constraint(K={last_k}) = {last_c:.3f}; rise = {rise:.3f}, "
            "monotone within tolerance. The lower boundary "
            "(sparse graphs near the trivial-zero theorem) and the upper "
            "boundary (dense graphs near the symmetric-neighbour theorem) "
            "are both reached by the swept Kauffman zoo, as predicted."
        )
    if rise > 0.2:
        return (
            f"[PARTIAL] constraint walks from {first_c:.3f} to {last_c:.3f} "
            "but the curve is not strictly monotone or does not reach both "
            "boundaries. Inspect per-seed."
        )
    return (
        f"[UNEXPECTED] constraint barely moved: {first_c:.3f} -> {last_c:.3f}. "
        "Density does not appear to drive the metric on this zoo; check "
        "the Kauffman wiring and the graph extraction."
    )


_DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "benchmarks"
    / "constraint_density_v0.6.1.csv"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the autonometrics constraint-density diagnostic."
    )
    default_rel = _DEFAULT_OUTPUT.relative_to(_DEFAULT_OUTPUT.parents[2])
    parser.add_argument(
        "--output",
        type=Path,
        default=_DEFAULT_OUTPUT,
        help=f"CSV output path (default: {default_rel}).",
    )
    parser.add_argument(
        "--n-nodes",
        type=int,
        default=_DEFAULT_N_NODES,
        help=f"Network size (default: {_DEFAULT_N_NODES}).",
    )
    parser.add_argument(
        "--n-seeds",
        type=int,
        default=_DEFAULT_N_SEEDS,
        help=f"Independent seeds per K (default: {_DEFAULT_N_SEEDS}).",
    )
    parser.add_argument(
        "--n-steps",
        type=int,
        default=_DEFAULT_N_STEPS,
        help=(
            "Trajectory length passed to KauffmanNetwork (default: "
            f"{_DEFAULT_N_STEPS}). The diagnostic only reads the causal "
            "graph, so this is kept at the minimum that the network "
            "constructor accepts."
        ),
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run a tiny subset (smoke mode).",
    )
    args = parser.parse_args(argv)

    if args.quick:
        k_values = _quick_k_values(args.n_nodes)
        n_seeds = _QUICK_N_SEEDS
    else:
        k_values = _default_k_values(args.n_nodes)
        n_seeds = args.n_seeds

    points = run_sweep(
        n_nodes=args.n_nodes,
        k_values=k_values,
        n_seeds=n_seeds,
        n_steps=args.n_steps,
    )

    print_table(points)
    write_csv(points, args.output)
    stats = aggregate(points)
    print_aggregate(stats)
    print()
    print(diagnosis_line(stats))
    print()
    print(f"CSV saved to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
