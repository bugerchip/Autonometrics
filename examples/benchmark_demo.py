"""Mini-benchmark for ``autonometrics`` v0.8.0a0.

Sweeps a curated set of systems whose autonomy structure is
independently understood (elementary cellular automata, random
Boolean networks at varying focal coupling, period-``p`` cycles,
the package's existing ``SimpleAutomaton`` and the new
``PromisedCycle`` adapter introduced for the CBA axis), measures
the **five** PBA axes ``(closure, memory, constraint, persistence,
coherence)`` for each, and reports:

- a per-system table on stdout,
- a CSV snapshot at ``docs/benchmarks/v0.8.0a0.csv`` (overridable
  via ``--output``),
- aggregate Pearson and Spearman correlations between every pair of
  the five axes (ten pairs in total),
- a quick-look diagnosis flag (``OK`` / ``WARN`` / ``FAIL``) keyed
  to the engineered-correlation thresholds spelt out in
  ``docs/PBA.md`` and ``docs/CBA.md``. The aggregate flag is the
  worst of the ten pairwise flags so a single overlap is enough to
  raise it.

Compared with v0.7.2a0, the changes are:

1. The fifth axis ``coherence`` (CBA, Theil-U style) is added to
   the meter and to the CSV. Adapters without a declarative layer
   (every adapter shipped before v0.8.0a0) score ``None`` for
   coherence and the orchestrator drops them out cleanly.
2. ``PromisedCycle`` is added to the zoo as the canonical
   CBA-positive substrate, with a sweep over ``p_noise`` and a
   single ``adversarial_shift`` configuration. Pre-registered
   per-mode predictions live in ``docs/CBA.md``.
3. The pairwise correlation table grows from six pairs to ten.
4. The default output path moves from ``v0.7.2a0.csv`` to
   ``v0.8.0a0.csv``.

Usage::

    python examples/benchmark_demo.py
    python examples/benchmark_demo.py --output results/run.csv
    python examples/benchmark_demo.py --quick     # tiny smoke subset
    python examples/benchmark_demo.py --n-seeds 5 # legacy v0.7.0a0 size

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

from autonometrics import Autonometer, PromisedCycle, SimpleAutomaton
from autonometrics.benchmarks import ECASystem, KauffmanNetwork, PeriodicCycle


@dataclass
class BenchmarkPoint:
    """One ``(closure, memory, constraint, persistence, coherence)`` measurement."""

    system_class: str
    params: str
    seed: int
    closure: float | None
    memory: float | None
    constraint: float | None
    persistence: float | None
    coherence: float | None
    quadrant: str
    notes: str


_ECA_RULES = (30, 90, 110, 184, 250)
_KAUFFMAN_COUPLINGS = (0.0, 0.33, 0.5, 0.67, 1.0)
_PERIODIC_PERIODS = (2, 4, 8)
_PROMISED_CONFIGS: tuple[tuple[int, int], ...] = (
    (2, 4),
    (4, 4),
    (4, 8),
)
_PROMISED_NOISES = (0.0, 0.25, 0.5, 0.75, 1.0)
_ADVERSARIAL_PERIOD = 4
_ADVERSARIAL_ALPHABET = 5
_N_STEPS = 2000
_DEFAULT_N_SEEDS = 30

_AXIS_FIELDS: tuple[str, ...] = (
    "closure",
    "memory",
    "constraint",
    "persistence",
    "coherence",
)

_PAIRS: tuple[tuple[str, str], ...] = (
    ("closure", "memory"),
    ("closure", "constraint"),
    ("closure", "persistence"),
    ("closure", "coherence"),
    ("memory", "constraint"),
    ("memory", "persistence"),
    ("memory", "coherence"),
    ("constraint", "persistence"),
    ("constraint", "coherence"),
    ("persistence", "coherence"),
)


def iter_systems(
    quick: bool = False, n_seeds: int = _DEFAULT_N_SEEDS
) -> Iterator[tuple[str, str, int, Any]]:
    """Yield ``(system_class, params, seed, system)`` tuples.

    With ``quick=True`` only three lightweight systems are emitted, so
    the smoke test exercises every code path without paying for the
    full sweep.

    ``n_seeds`` controls how many random seeds are explored per
    parameter setting. Periodic cycles use ``max(3, n_seeds // 2)``
    seeds since they have less stochastic structure to exercise.
    Adapter classes and parameter values themselves are kept fixed
    across versions; only ``n_seeds`` is dialled up to grow the
    sample (per ``docs/ATLAS_GEOMETRY.md``).
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
        yield (
            "PromisedCycle",
            "period=4,alphabet=4,p_noise=0.25",
            0,
            PromisedCycle(
                length=_N_STEPS,
                period=4,
                alphabet=4,
                p_noise=0.25,
                seed=0,
            ),
        )
        return

    if n_seeds < 1:
        raise ValueError(f"n_seeds must be >= 1, got {n_seeds!r}")

    periodic_seeds = max(3, n_seeds // 2)

    for rule in _ECA_RULES:
        for seed in range(n_seeds):
            yield (
                "ECASystem",
                f"rule={rule}",
                seed,
                ECASystem(rule=rule, n_steps=_N_STEPS, width=51, seed=seed),
            )

    for coupling in _KAUFFMAN_COUPLINGS:
        for seed in range(n_seeds):
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
        for seed in range(periodic_seeds):
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
    for seed in range(n_seeds):
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

    promised_seeds = max(3, n_seeds // 2)
    for period, alphabet in _PROMISED_CONFIGS:
        for p_noise in _PROMISED_NOISES:
            for seed in range(promised_seeds):
                yield (
                    "PromisedCycle",
                    f"period={period},alphabet={alphabet},p_noise={p_noise}",
                    seed,
                    PromisedCycle(
                        length=_N_STEPS,
                        period=period,
                        alphabet=alphabet,
                        mode="random_noise",
                        p_noise=p_noise,
                        seed=seed,
                    ),
                )
    for seed in range(promised_seeds):
        yield (
            "PromisedCycle",
            f"adversarial,period={_ADVERSARIAL_PERIOD}",
            seed,
            PromisedCycle(
                length=_N_STEPS,
                period=_ADVERSARIAL_PERIOD,
                alphabet=_ADVERSARIAL_ALPHABET,
                mode="adversarial_shift",
                seed=seed,
            ),
        )


def quadrant_of(closure: float | None, memory: float | None) -> str:
    """Map a ``(closure, memory)`` pair to one of four named quadrants.

    The quadrant naming is preserved from v0.5.x for backwards
    compatibility with the existing scatter plot. The third axis
    (``constraint``) is reported alongside the quadrant but does not
    enter the categorisation.
    """
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


def measure_safe(
    meter: Autonometer, system: Any
) -> tuple[
    float | None,
    float | None,
    float | None,
    float | None,
    float | None,
    str,
]:
    """Run ``meter.measure`` and turn ``ValueError`` into a recorded note.

    Degenerate trajectories (constant series, zero conditional entropy,
    too-short sequences, near-constant focal marginals) are a known
    property of some benchmark systems; the demo records them rather
    than aborting.
    """
    try:
        profile = meter.measure(system)
    except ValueError as exc:
        return None, None, None, None, None, _truncate(str(exc))
    return (
        profile.ratio_endo_total,
        profile.memory_endo_ratio,
        profile.constraint_closure,
        profile.rai_proxy_persistence,
        profile.cba_theil_u,
        "",
    )


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


def _aggregate_flag(flags: dict[str, str]) -> str:
    """Worst of three pairwise diagnosis flags."""
    rank = {"OK": 0, "WARN": 1, "FAIL": 2, "N/A": -1}
    if not flags:
        return "N/A"
    valid = [(rank[v], v) for v in flags.values() if v != "N/A"]
    if not valid:
        return "N/A"
    return max(valid)[1]


def run_benchmark(quick: bool = False, n_seeds: int = _DEFAULT_N_SEEDS) -> list[BenchmarkPoint]:
    """Generate every system, measure it, and return the list of points.

    ``n_seeds`` is forwarded to :func:`iter_systems` and ignored when
    ``quick`` is set.
    """
    meter = Autonometer(
        metrics=[
            "albantakis",
            "memory",
            "constraint_closure",
            "persistence",
            "coherence",
        ]
    )
    points: list[BenchmarkPoint] = []
    for system_class, params, seed, system in iter_systems(quick=quick, n_seeds=n_seeds):
        closure, memory, constraint, persistence, coherence, notes = measure_safe(meter, system)
        points.append(
            BenchmarkPoint(
                system_class=system_class,
                params=params,
                seed=seed,
                closure=closure,
                memory=memory,
                constraint=constraint,
                persistence=persistence,
                coherence=coherence,
                quadrant=quadrant_of(closure, memory),
                notes=notes,
            )
        )
    return points


def print_table(points: list[BenchmarkPoint]) -> None:
    """Pretty-print one row per benchmark point on stdout."""
    fmt = "{:<18} {:<28} {:>4} {:>10} {:>10} {:>10} {:>11} {:>10} {:<14} {}"
    print(
        fmt.format(
            "class",
            "params",
            "seed",
            "closure",
            "memory",
            "constraint",
            "persistence",
            "coherence",
            "quadrant",
            "notes",
        )
    )
    print(
        fmt.format(
            "-" * 18,
            "-" * 28,
            "----",
            "-" * 10,
            "-" * 10,
            "-" * 10,
            "-" * 11,
            "-" * 10,
            "-" * 14,
            "-" * 30,
        )
    )
    for p in points:
        c = "n/a" if p.closure is None else f"{p.closure:.4f}"
        m = "n/a" if p.memory is None else f"{p.memory:.4f}"
        cc = "n/a" if p.constraint is None else f"{p.constraint:.4f}"
        pp = "n/a" if p.persistence is None else f"{p.persistence:.4f}"
        co = "n/a" if p.coherence is None else f"{p.coherence:.4f}"
        print(
            fmt.format(
                p.system_class,
                p.params,
                p.seed,
                c,
                m,
                cc,
                pp,
                co,
                p.quadrant,
                p.notes,
            )
        )


_CSV_FIELDS = [
    "class",
    "params",
    "seed",
    "closure",
    "memory",
    "constraint",
    "persistence",
    "coherence",
    "quadrant",
    "notes",
]


def write_csv(points: list[BenchmarkPoint], path: Path) -> None:
    """Persist the benchmark points to ``path`` as a UTF-8 CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        for p in points:
            row = asdict(p)
            row["class"] = row.pop("system_class")
            for key in _AXIS_FIELDS:
                row[key] = "" if row[key] is None else f"{row[key]:.6f}"
            writer.writerow(row)


def _column(points: list[BenchmarkPoint], name: str) -> list[float | None]:
    return [getattr(p, name) for p in points]


def _pair_array(points: list[BenchmarkPoint], a: str, b: str) -> tuple[np.ndarray, np.ndarray]:
    """Return paired arrays of axis ``a`` and ``b`` for points where both are not ``None``."""
    xs: list[float] = []
    ys: list[float] = []
    for p in points:
        ax = getattr(p, a)
        bx = getattr(p, b)
        if ax is None or bx is None:
            continue
        xs.append(float(ax))
        ys.append(float(bx))
    return np.asarray(xs, dtype=float), np.asarray(ys, dtype=float)


def summarise(points: list[BenchmarkPoint]) -> dict[str, Any]:
    """Compute aggregate stats over the (valid) measurements."""
    n_total = len(points)
    n_valid_full = sum(
        1 for p in points if all(getattr(p, axis) is not None for axis in _AXIS_FIELDS)
    )

    correlations: dict[str, dict[str, float | str | int]] = {}
    for a, b in _PAIRS:
        x, y = _pair_array(points, a, b)
        n = int(x.size)
        if n >= 2:
            r_p = pearson(x, y)
            r_s = spearman(x, y)
        else:
            r_p = float("nan")
            r_s = float("nan")
        flag = diagnosis_flag(abs(r_p)) if not np.isnan(r_p) else "N/A"
        correlations[f"{a}-{b}"] = {
            "n": n,
            "pearson": r_p,
            "spearman": r_s,
            "flag": flag,
        }

    flags = {k: str(v["flag"]) for k, v in correlations.items()}
    aggregate = _aggregate_flag(flags)

    counts: dict[str, int] = {}
    for p in points:
        counts[p.quadrant] = counts.get(p.quadrant, 0) + 1

    return {
        "n_total": n_total,
        "n_valid": n_valid_full,
        "n_dropped": n_total - n_valid_full,
        "correlations": correlations,
        "flag": aggregate,
        "quadrants": counts,
    }


def print_summary(summary: dict[str, Any]) -> None:
    """Pretty-print the aggregate stats and the diagnosis line."""
    print()
    print(
        f"Sample size: {summary['n_valid']}/{summary['n_total']} fully-valid points "
        f"(dropped: {summary['n_dropped']})"
    )
    print()
    print("Pairwise correlations:")
    print(f"  {'pair':<22} {'n':>4} {'pearson':>10} {'spearman':>10} {'flag':<6}")
    print(f"  {'-' * 22} {'-' * 4} {'-' * 10} {'-' * 10} {'-' * 6}")
    for name, stats in summary["correlations"].items():
        r_p = stats["pearson"]
        r_s = stats["spearman"]
        n = stats["n"]
        flag = stats["flag"]
        rp_str = "  n/a" if isinstance(r_p, float) and np.isnan(r_p) else f"{r_p:+.4f}"
        rs_str = "  n/a" if isinstance(r_s, float) and np.isnan(r_s) else f"{r_s:+.4f}"
        print(f"  {name:<22} {n:>4} {rp_str:>10} {rs_str:>10} {flag:<6}")
    print()
    print(f"Aggregate diagnosis: {summary['flag']}")
    print()
    print("Quadrant distribution (closure x memory only):")
    for q in ("drift", "clockwork", "turbulence", "autopoietic", "n/a"):
        print(f"  {q:<14} {summary['quadrants'].get(q, 0):>3}")
    print()
    flag = summary["flag"]
    if flag == "OK":
        print(
            "[OK] All pairwise |r| < 0.7 - the three axes carry distinct "
            "information; safe to extend the roadmap."
        )
    elif flag == "WARN":
        print(
            "[WARN] At least one pair sits in 0.7 <= |r| < 0.9 - review whether "
            "those axes overlap structurally before adding more."
        )
    elif flag == "FAIL":
        print(
            "[FAIL] At least one pair has |r| >= 0.9 - engineered correlation "
            "suspected; pause and audit before adding more axes (see docs/PBA.md)."
        )
    else:
        print("[N/A] Not enough valid points to compute correlations.")


_DEFAULT_OUTPUT = Path(__file__).resolve().parent.parent / "docs" / "benchmarks" / "v0.8.0a0.csv"


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
    parser.add_argument(
        "--n-seeds",
        type=int,
        default=_DEFAULT_N_SEEDS,
        help=(
            f"Number of seeds per parameter setting (default: {_DEFAULT_N_SEEDS}). "
            "Use 5 to reproduce the v0.7.0a0 snapshot. Ignored under --quick."
        ),
    )
    args = parser.parse_args(argv)

    points = run_benchmark(quick=args.quick, n_seeds=args.n_seeds)
    print_table(points)
    write_csv(points, args.output)
    summary = summarise(points)
    print_summary(summary)
    print(f"\nCSV saved to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
