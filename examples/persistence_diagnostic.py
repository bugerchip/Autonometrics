"""Persistence diagnostic: how does the metric react to focal coupling?

Background
----------
The persistence axis shipped in ``v0.7.0a0`` measures the fraction
of a single-bit perturbation that the system absorbs as it follows
its own dynamics, normalised against the chance baseline of two
independent random trajectories of the same focal alphabet. The
metric formalises the Lee & McShea (2020) notion of *persistence*
adapted to systems without an externally specified goal.

A clean controllable knob for the metric is the **focal coupling**
of a Kauffman NK boolean network. The naive expectation is a
monotone rise from "low persistence at coupling = 0" to "high
persistence at coupling = 1". Running the diagnostic falsifies that
expectation and reveals a more interesting shape with two distinct
*trivial-absorption* boundary regimes flanking a non-trivial middle.
The first run of the diagnostic on a 10-node, k = 3 zoo shows:

- **Low-coupling boundary (coupling near 0).** When all of the
  focal's inputs are the focal itself, the focal evolves under a
  1-bit boolean rule. Most seeds collapse to a constant trajectory
  in one step (``focal_marginal`` becomes near-degenerate; the
  seed is dropped). The handful of seeds whose 1-bit rule keeps
  the trajectory non-constant happen to score
  ``persistence approx 1`` — not because the system *defends* its
  course, but because the focal value falls into a fixed point
  one step after the perturbation is applied. The high score is
  therefore a **trivial-absorption** signature, not an autonomy
  signature, and the diagnostic is deliberately honest about it.
- **High-coupling boundary (coupling near 1).** When none of the
  focal's inputs is the focal itself, a flip of the focal bit at
  ``t_star`` is invisible to the rule that computes the focal at
  ``t_star + 1``. The metric returns ``persistence approx 1`` by
  construction; this is again *trivial absorption*, of a different
  kind (the perturbation never enters the dynamics at all).
- **Non-trivial middle (intermediate coupling).** When the focal's
  inputs include both itself and other nodes, perturbations
  actually propagate through the network and the metric
  discriminates seed-to-seed structure. This is the regime in
  which the metric carries meaningful autonomy information.

The U-shape is the persistence analogue of the closure-saturation
wall at determinism + full observability documented in ``v0.5.1a0``
and the symmetric-neighbour saturation theorem documented in
``v0.6.1a0``: the metric has structurally trivial regions at the
edges of its parameter space and a non-trivial *useful range* in
the middle. The diagnostic therefore mirrors the same maintenance
pattern: ship the metric with its domain-of-applicability shape
visible, and document the boundary theorems in a follow-up
maintenance cycle (planned for ``v0.7.1`` together with the
perturbation-magnitude sweep).

Method
------
For each value ``coupling`` in a sweep (default ``0.0, 0.1, ...,
1.0``) the diagnostic generates ``n_seeds`` independent Kauffman
networks with ``n_nodes`` binary nodes and a fixed in-degree
``k``. The focal-node trajectory and the env-node trajectory are
extracted, the orchestrator computes ``persistence`` via
``replay_from_perturbation``, and the per-seed scores are reduced
to ``mean +/- std`` per coupling level.

Outputs
-------
- A per-row table on stdout.
- A CSV at ``docs/benchmarks/persistence_v0.7.0.csv`` (overridable
  via ``--output``).
- An aggregate summary table with ``mean +/- std`` of persistence
  per coupling level.
- A diagnosis line that flags whether the curve walks from a low
  / mixed regime at small coupling to ``persistence approx 1`` at
  full external coupling.

Usage
-----
::

    python examples/persistence_diagnostic.py
    python examples/persistence_diagnostic.py --quick
    python examples/persistence_diagnostic.py --n-nodes 12 --n-seeds 5

The script is numpy-only; rendering the optional curve figure
lives in ``examples/persistence_plot.py``.
"""

from __future__ import annotations

import argparse
import csv
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from autonometrics import Autonometer
from autonometrics.benchmarks import KauffmanNetwork

_DEFAULT_COUPLINGS: tuple[float, ...] = (
    0.0,
    0.1,
    0.2,
    0.3,
    0.4,
    0.5,
    0.6,
    0.7,
    0.8,
    0.9,
    1.0,
)
_QUICK_COUPLINGS: tuple[float, ...] = (0.0, 0.5, 1.0)
_DEFAULT_N_NODES = 10
_DEFAULT_K = 3
_DEFAULT_N_STEPS = 600
_DEFAULT_N_SEEDS = 10
_QUICK_N_SEEDS = 3


@dataclass
class PersistencePoint:
    """A single ``(coupling, seed) -> persistence`` measurement."""

    coupling: float
    seed: int
    persistence: float | None
    notes: str


def _truncate(text: str, length: int = 80) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= length:
        return cleaned
    return cleaned[: length - 3] + "..."


def iter_configs(
    couplings: tuple[float, ...],
    n_seeds: int,
    n_nodes: int,
    k: int,
    n_steps: int,
) -> Iterator[tuple[float, int, KauffmanNetwork]]:
    """Yield ``(coupling, seed, system)`` tuples for the sweep."""
    for coupling in couplings:
        for seed in range(n_seeds):
            yield coupling, seed, KauffmanNetwork(
                n_nodes=n_nodes,
                k=k,
                n_steps=n_steps,
                coupling=coupling,
                seed=seed,
            )


def measure_safe(meter: Autonometer, system: KauffmanNetwork) -> tuple[float | None, str]:
    """Run ``meter.measure`` and turn ``ValueError`` into a recorded note.

    Some Kauffman seeds at ``coupling = 0`` produce focal trajectories
    that are constant after a single step (the focal node's 1-input
    rule reaches a fixed point). The persistence metric raises a
    ``ValueError`` in that case because ``d_ref`` collapses; the
    diagnostic records the note and aggregates only the valid
    seeds, matching the pattern used by the saturation and
    constraint-density diagnostics.
    """
    try:
        profile = meter.measure(system)
    except ValueError as exc:
        return None, _truncate(str(exc))
    return profile.rai_proxy_persistence, ""


def run_sweep(
    couplings: tuple[float, ...] = _DEFAULT_COUPLINGS,
    n_seeds: int = _DEFAULT_N_SEEDS,
    n_nodes: int = _DEFAULT_N_NODES,
    k: int = _DEFAULT_K,
    n_steps: int = _DEFAULT_N_STEPS,
) -> list[PersistencePoint]:
    """Sweep ``couplings`` against ``n_seeds`` and collect points."""
    meter = Autonometer(metrics=["persistence"])
    points: list[PersistencePoint] = []
    for coupling, seed, system in iter_configs(couplings, n_seeds, n_nodes, k, n_steps):
        score, notes = measure_safe(meter, system)
        points.append(
            PersistencePoint(
                coupling=coupling,
                seed=seed,
                persistence=score,
                notes=notes,
            )
        )
    return points


def print_table(points: list[PersistencePoint]) -> None:
    """Pretty-print one row per measurement."""
    fmt = "{:>9} {:>4} {:>12} {}"
    print(fmt.format("coupling", "seed", "persistence", "notes"))
    print(fmt.format("-" * 9, "----", "-" * 12, "-" * 30))
    for p in points:
        s = "n/a" if p.persistence is None else f"{p.persistence:.4f}"
        print(fmt.format(f"{p.coupling:.2f}", p.seed, s, p.notes))


_CSV_FIELDS = ["coupling", "seed", "persistence", "notes"]


def write_csv(points: list[PersistencePoint], path: Path) -> None:
    """Persist the diagnostic points to ``path`` as a UTF-8 CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        for p in points:
            row = asdict(p)
            row["coupling"] = f"{row['coupling']:.4f}"
            row["persistence"] = (
                "" if row["persistence"] is None else f"{row['persistence']:.6f}"
            )
            writer.writerow(row)


def aggregate(points: list[PersistencePoint]) -> dict[float, dict[str, Any]]:
    """Reduce per-seed measurements to ``mean +/- std`` per coupling."""
    by_c: dict[float, list[PersistencePoint]] = {}
    for p in points:
        by_c.setdefault(p.coupling, []).append(p)

    out: dict[float, dict[str, Any]] = {}
    for c_value, group in sorted(by_c.items()):
        valid = [g for g in group if g.persistence is not None]
        if valid:
            scores = np.array([g.persistence for g in valid], dtype=float)
            out[c_value] = {
                "n_total": len(group),
                "n_valid": len(valid),
                "mean": float(np.mean(scores)),
                "std": float(np.std(scores)),
            }
        else:
            out[c_value] = {
                "n_total": len(group),
                "n_valid": 0,
                "mean": float("nan"),
                "std": float("nan"),
            }
    return out


def print_aggregate(stats: dict[float, dict[str, Any]]) -> None:
    """Pretty-print the per-coupling aggregate stats."""
    print()
    print("Aggregate (mean +/- std per coupling):")
    fmt = "{:>9} {:>5} {:>20}"
    print(fmt.format("coupling", "n", "persistence"))
    print(fmt.format("-" * 9, "-" * 5, "-" * 20))
    for c_value, row in stats.items():
        if row["n_valid"] == 0:
            s_str = "n/a"
        else:
            s_str = f"{row['mean']:.4f} +/- {row['std']:.4f}"
        print(fmt.format(f"{c_value:.2f}", f"{row['n_valid']}/{row['n_total']}", s_str))


def diagnosis_line(stats: dict[float, dict[str, Any]]) -> str:
    """Return a single-line verdict on the shape of the persistence curve.

    The diagnostic does *not* expect a monotone rise. It expects a
    **U-shape**: the curve should sit near the upper boundary at
    both ends of the focal-coupling axis (trivial absorption: by
    fixed-point collapse on the left, by flip-invisibility on the
    right), and dip in the middle, where the metric carries
    non-trivial structural information. The verdict reports whether
    that U-shape is observed and where the dip is located.
    """
    couplings = sorted(stats.keys())
    means = [stats[c]["mean"] for c in couplings]
    valid = [(c, m) for c, m in zip(couplings, means, strict=True) if not np.isnan(m)]
    if len(valid) < 3:
        return "[N/A] not enough valid coupling levels to assess shape."

    first_c, first_m = valid[0]
    last_c, last_m = valid[-1]

    min_idx = int(np.argmin([m for _, m in valid]))
    min_c, min_m = valid[min_idx]
    max_m = max(m for _, m in valid)

    edges_high = first_m >= 0.6 and last_m >= 0.6
    middle_dip = min_idx not in (0, len(valid) - 1)
    dip_size = ((first_m + last_m) / 2.0) - min_m

    if edges_high and middle_dip and dip_size > 0.10:
        return (
            f"[OK] U-shape observed: persistence({first_c:.2f}) = {first_m:.3f}, "
            f"min at coupling = {min_c:.2f} ({min_m:.3f}), "
            f"persistence({last_c:.2f}) = {last_m:.3f}; dip = {dip_size:.3f}. "
            "Both boundary regimes (low coupling: focal collapses to fixed "
            "point; high coupling: focal flip invisible to its own rule) "
            "produce trivial absorption. The non-trivial useful range of "
            "the metric on Kauffman networks lies in the intermediate "
            "couplings, where actual perturbation propagation is observed."
        )
    if dip_size > 0.05:
        return (
            f"[PARTIAL] curve has a dip in the middle (max {max_m:.3f}, "
            f"min {min_m:.3f} at coupling = {min_c:.2f}) but the boundary "
            "regimes are not both saturated, or the dip is shallow. The "
            "boundary-theorem story is partially supported; per-seed "
            "inspection recommended before formalising it in v0.7.1."
        )
    return (
        f"[UNEXPECTED] curve does not match the expected U-shape "
        f"(persistence({first_c:.2f}) = {first_m:.3f}, min {min_m:.3f}, "
        f"persistence({last_c:.2f}) = {last_m:.3f}). The two boundary "
        "regimes documented in the v0.7.0a0 design did not produce "
        "trivial absorption on this run; this is a finding that "
        "deserves follow-up before promoting the diagnostic."
    )


_DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "benchmarks"
    / "persistence_v0.7.0.csv"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the autonometrics persistence diagnostic."
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
        help=f"Number of nodes per Kauffman network (default: {_DEFAULT_N_NODES}).",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=_DEFAULT_K,
        help=f"In-degree per node (default: {_DEFAULT_K}).",
    )
    parser.add_argument(
        "--n-seeds",
        type=int,
        default=_DEFAULT_N_SEEDS,
        help=f"Independent seeds per coupling (default: {_DEFAULT_N_SEEDS}).",
    )
    parser.add_argument(
        "--n-steps",
        type=int,
        default=_DEFAULT_N_STEPS,
        help=f"Trajectory length (default: {_DEFAULT_N_STEPS}).",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run a tiny subset (smoke mode).",
    )
    args = parser.parse_args(argv)

    if args.quick:
        couplings = _QUICK_COUPLINGS
        n_seeds = _QUICK_N_SEEDS
    else:
        couplings = _DEFAULT_COUPLINGS
        n_seeds = args.n_seeds

    points = run_sweep(
        couplings=couplings,
        n_seeds=n_seeds,
        n_nodes=args.n_nodes,
        k=args.k,
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
