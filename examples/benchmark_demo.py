"""Mini-benchmark for ``autonometrics`` v0.5.0a0.

Sweeps a curated set of systems whose autonomy structure is
independently understood (elementary cellular automata, random Boolean
networks at varying focal coupling, period-``p`` cycles, and the
package's existing ``SimpleAutomaton``), measures
``(closure, memory)`` for each, and reports:

- a per-system table on stdout,
- a CSV snapshot at ``docs/benchmarks/v0.5.0a0.csv`` (overridable
  via ``--output``),
- aggregate Pearson and Spearman correlations between the two axes,
- a quick-look diagnosis flag (``OK`` / ``WARN`` / ``FAIL``) keyed
  to the engineered-correlation thresholds spelt out in
  ``docs/PBA.md``.

Usage::

    python examples/benchmark_demo.py
    python examples/benchmark_demo.py --output results/run.csv
    python examples/benchmark_demo.py --quick     # tiny smoke subset

The script is intentionally numpy-only and adds no new runtime
dependency. It is a *consumer* of ``autonometrics``; it imports the
public API and the ``benchmarks`` subpackage but does not extend
either.
"""

from __future__ import annotations

import argparse
import csv
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from autonometrics import Autonometer, SimpleAutomaton
from autonometrics.benchmarks import ECASystem, KauffmanNetwork, PeriodicCycle


@dataclass
class BenchmarkPoint:
    """A single ``(closure, memory)`` measurement on one system."""

    system_class: str
    params: str
    seed: int
    closure: float | None
    memory: float | None
    quadrant: str
    notes: str


_ECA_RULES = (30, 90, 110, 184, 250)
_KAUFFMAN_COUPLINGS = (0.0, 0.33, 0.5, 0.67, 1.0)
_PERIODIC_PERIODS = (2, 4, 8)
_N_STEPS = 2000


def iter_systems(quick: bool = False) -> Iterator[tuple[str, str, int, Any]]:
    """Yield ``(system_class, params, seed, system)`` tuples.

    With ``quick=True`` only three lightweight systems are emitted, so
    the smoke test exercises every code path without paying for the
    full sweep.
    """
    if quick:
        yield (
            "ECASystem",
            "rule=110",
            0,
            ECASystem(rule=110, n_steps=_N_STEPS, width=51, seed=0),
        )
        yield (
            "KauffmanNetwork",
            "coupling=0.5",
            0,
            KauffmanNetwork(n_nodes=10, k=3, n_steps=_N_STEPS, coupling=0.5, seed=0),
        )
        yield (
            "PeriodicCycle",
            "period=4",
            0,
            PeriodicCycle(period=4, n_steps=_N_STEPS, env_alphabet=3, seed=0),
        )
        return

    for rule in _ECA_RULES:
        for seed in range(5):
            yield (
                "ECASystem",
                f"rule={rule}",
                seed,
                ECASystem(rule=rule, n_steps=_N_STEPS, width=51, seed=seed),
            )

    for coupling in _KAUFFMAN_COUPLINGS:
        for seed in range(5):
            yield (
                "KauffmanNetwork",
                f"coupling={coupling}",
                seed,
                KauffmanNetwork(
                    n_nodes=10,
                    k=3,
                    n_steps=_N_STEPS,
                    coupling=coupling,
                    seed=seed,
                ),
            )

    for period in _PERIODIC_PERIODS:
        for seed in range(3):
            yield (
                "PeriodicCycle",
                f"period={period}",
                seed,
                PeriodicCycle(
                    period=period,
                    n_steps=_N_STEPS,
                    env_alphabet=3,
                    seed=seed,
                ),
            )

    rng = np.random.default_rng(0)
    env = rng.integers(0, 3, size=_N_STEPS).astype(np.int64)
    for seed in range(5):
        yield (
            "SimpleAutomaton",
            "self_generated",
            seed,
            SimpleAutomaton.from_self_generated_rules(n_states=4, env=env, seed=seed),
        )
        yield (
            "SimpleAutomaton",
            "external",
            seed,
            SimpleAutomaton.from_external_rules(n_states=4, env=env, seed=seed),
        )


def quadrant_of(closure: float | None, memory: float | None) -> str:
    """Map a ``(closure, memory)`` pair to one of four named quadrants."""
    if closure is None or memory is None:
        return "n/a"
    c_high = closure >= 0.5
    m_high = memory >= 0.5
    if c_high and m_high:
        return "autopoietic"
    if c_high:
        return "clockwork"
    if m_high:
        return "turbulence"
    return "drift"


def measure_safe(meter: Autonometer, system: Any) -> tuple[float | None, float | None, str]:
    """Run ``meter.measure`` and turn ``ValueError`` into a recorded note.

    Degenerate trajectories (constant series, zero conditional entropy,
    too-short sequences) are a known property of some benchmark
    systems; the demo records them rather than aborting.
    """
    try:
        profile = meter.measure(system)
    except ValueError as exc:
        return None, None, _truncate(str(exc))
    return profile.ratio_endo_total, profile.memory_endo_ratio, ""


def _truncate(text: str, length: int = 80) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= length:
        return cleaned
    return cleaned[: length - 3] + "..."


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    """Pearson correlation; ``nan`` if the sample is too small or constant."""
    if x.size < 2:
        return float("nan")
    if np.std(x) <= 0 or np.std(y) <= 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman rank correlation, computed as Pearson on rank-transformed inputs."""
    if x.size < 2:
        return float("nan")
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return pearson(rx, ry)


def diagnosis_flag(abs_r: float) -> str:
    """Map ``|r|`` to one of three discrete flags following ``docs/PBA.md``."""
    if np.isnan(abs_r):
        return "N/A"
    if abs_r < 0.7:
        return "OK"
    if abs_r < 0.9:
        return "WARN"
    return "FAIL"


def run_benchmark(quick: bool = False) -> list[BenchmarkPoint]:
    """Generate every system, measure it, and return the list of points."""
    meter = Autonometer(metrics=["albantakis", "memory"])
    points: list[BenchmarkPoint] = []
    for system_class, params, seed, system in iter_systems(quick=quick):
        closure, memory, notes = measure_safe(meter, system)
        points.append(
            BenchmarkPoint(
                system_class=system_class,
                params=params,
                seed=seed,
                closure=closure,
                memory=memory,
                quadrant=quadrant_of(closure, memory),
                notes=notes,
            )
        )
    return points


def print_table(points: list[BenchmarkPoint]) -> None:
    """Pretty-print one row per benchmark point on stdout."""
    fmt = "{:<18} {:<22} {:>4} {:>10} {:>10} {:<14} {}"
    print(fmt.format("class", "params", "seed", "closure", "memory", "quadrant", "notes"))
    print(fmt.format("-" * 18, "-" * 22, "----", "-" * 10, "-" * 10, "-" * 14, "-" * 30))
    for p in points:
        c = "n/a" if p.closure is None else f"{p.closure:.4f}"
        m = "n/a" if p.memory is None else f"{p.memory:.4f}"
        print(fmt.format(p.system_class, p.params, p.seed, c, m, p.quadrant, p.notes))


_CSV_FIELDS = ["class", "params", "seed", "closure", "memory", "quadrant", "notes"]


def write_csv(points: list[BenchmarkPoint], path: Path) -> None:
    """Persist the benchmark points to ``path`` as a UTF-8 CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        for p in points:
            row = asdict(p)
            row["class"] = row.pop("system_class")
            row["closure"] = "" if row["closure"] is None else f"{row['closure']:.6f}"
            row["memory"] = "" if row["memory"] is None else f"{row['memory']:.6f}"
            writer.writerow(row)


def summarise(points: list[BenchmarkPoint]) -> dict[str, Any]:
    """Compute aggregate stats over the (valid) measurements."""
    valid = [p for p in points if p.closure is not None and p.memory is not None]
    n_valid = len(valid)
    n_total = len(points)

    if n_valid >= 2:
        closures = np.array([p.closure for p in valid], dtype=float)
        memories = np.array([p.memory for p in valid], dtype=float)
        r_p = pearson(closures, memories)
        r_s = spearman(closures, memories)
    else:
        r_p = float("nan")
        r_s = float("nan")

    counts: dict[str, int] = {}
    for p in points:
        counts[p.quadrant] = counts.get(p.quadrant, 0) + 1

    return {
        "n_total": n_total,
        "n_valid": n_valid,
        "n_dropped": n_total - n_valid,
        "pearson": r_p,
        "spearman": r_s,
        "flag": diagnosis_flag(abs(r_p)) if not np.isnan(r_p) else "N/A",
        "quadrants": counts,
    }


def print_summary(summary: dict[str, Any]) -> None:
    """Pretty-print the aggregate stats and the diagnosis line."""
    print()
    print(
        f"Sample size: {summary['n_valid']}/{summary['n_total']} valid points "
        f"(dropped: {summary['n_dropped']})"
    )
    print(f"Pearson r  : {summary['pearson']:+.4f}")
    print(f"Spearman r : {summary['spearman']:+.4f}")
    print(f"Diagnosis  : {summary['flag']}")
    print()
    print("Quadrant distribution:")
    for q in ("drift", "clockwork", "turbulence", "autopoietic", "n/a"):
        print(f"  {q:<14} {summary['quadrants'].get(q, 0):>3}")
    print()
    flag = summary["flag"]
    if flag == "OK":
        print(
            "[OK] |r| < 0.7 - closure and memory carry distinct information; "
            "safe to extend the roadmap to v0.6+."
        )
    elif flag == "WARN":
        print(
            "[WARN] 0.7 <= |r| < 0.9 - review whether the two metrics overlap "
            "structurally before adding more axes."
        )
    elif flag == "FAIL":
        print(
            "[FAIL] |r| >= 0.9 - engineered correlation suspected; pause and "
            "audit before adding more axes (see docs/PBA.md)."
        )
    else:
        print("[N/A] Not enough valid points to compute a correlation.")


_DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent.parent / "docs" / "benchmarks" / "v0.5.0a0.csv"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the autonometrics mini-benchmark.")
    default_rel = _DEFAULT_OUTPUT.relative_to(_DEFAULT_OUTPUT.parents[2])
    parser.add_argument(
        "--output",
        type=Path,
        default=_DEFAULT_OUTPUT,
        help=f"CSV output path (default: {default_rel}).",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run a tiny subset (smoke mode).",
    )
    args = parser.parse_args(argv)

    points = run_benchmark(quick=args.quick)
    print_table(points)
    write_csv(points, args.output)
    summary = summarise(points)
    print_summary(summary)
    print(f"\nCSV saved to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
