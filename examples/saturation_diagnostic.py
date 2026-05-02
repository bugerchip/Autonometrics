"""Saturation diagnostic: how does Albantakis closure react to injected noise?

Background
----------
The reference benchmark shipped in ``v0.5.0a0`` left a visible
signature on the autonomy plane: every elementary cellular
automaton, every period-``p`` cycle and every self-generated
``SimpleAutomaton`` in the zoo collapsed onto the vertical line
``closure = 1.0``. The ``v0.5.0a0`` release notes documented this
as a property of the current adapter zoo, not of the metric pair.

Closer inspection makes the underlying reason explicit. The
Albantakis closure score is

.. math::

    A \\;=\\; \\frac{I(S_{t+1};\\,S_t \\mid E_t)}{H(S_{t+1} \\mid E_t)}

If the system's transition is **deterministic** and the pair
``(S_t, E_t)`` already contains every variable the rule depends on,
then ``H(S_{t+1} | S_t, E_t) = 0`` and, by the chain rule,
``I(S_{t+1}; S_t | E_t) = H(S_{t+1} | E_t)``. The numerator and the
denominator are equal by construction, so ``A = 1`` is forced.
The "wall" at ``closure = 1.0`` is therefore a **theorem about the
metric on a class of systems**, not an empirical accident.

This script tests that prediction by **injecting controlled
observation noise** into a known-saturating system (rule 110) and
measuring how the closure score reacts. If the saturation is
indeed driven by determinism plus full observability, then breaking
either one with a small probability of bit-flip should pull
closure off the wall in a smooth, monotonic way.

Method
------
For each noise level ``p`` in a fixed sweep, the focal-cell
trajectory of an elementary cellular automaton (rule 110, default)
is run through a Bernoulli bit-flipper with parameter ``p``.
The environment trajectory is **left untouched**: the diagnostic
deliberately probes "noise added to the system's own observation",
not "noise in the environment".

Per noise level we run a handful of independent seeds so that
each row in the output is a clean ``(p, seed) -> (closure, memory)``
record, and the aggregate report reduces them to mean ± std per ``p``.

Outputs
-------
- A per-row table on stdout.
- A CSV at ``docs/benchmarks/saturation_v0.5.1.csv``
  (overridable via ``--output``).
- An aggregate summary table with mean ± std of closure and memory
  per noise level.

Usage
-----
::

    python examples/saturation_diagnostic.py
    python examples/saturation_diagnostic.py --quick
    python examples/saturation_diagnostic.py --rule 30 --n-seeds 3

The script is numpy-only; rendering the optional curve figure
lives in ``examples/saturation_plot.py``.
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
from autonometrics.benchmarks import ECASystem

_DEFAULT_NOISE_LEVELS = (0.0, 0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50)
_QUICK_NOISE_LEVELS = (0.0, 0.10, 0.30)
_DEFAULT_RULE = 110
_DEFAULT_N_STEPS = 2000
_DEFAULT_WIDTH = 51
_DEFAULT_N_SEEDS = 5
_QUICK_N_SEEDS = 2
_NOISE_SEED_OFFSET = 100_000


@dataclass
class SaturationPoint:
    """A single ``(p_noise, seed) -> (closure, memory)`` measurement."""

    rule: int
    p_noise: float
    seed: int
    closure: float | None
    memory: float | None
    notes: str


class NoisyECA:
    """Wrap an :class:`ECASystem` and bit-flip its focal trajectory.

    The environment is reproduced verbatim; only the focal-cell state
    history is corrupted, with each timestep flipped independently
    with probability ``p_noise``. The wrapper satisfies the
    ``AutonomySystem`` protocol expected by :class:`Autonometer`.

    The bit-flip RNG is seeded independently from the underlying ECA
    RNG so that the noise pattern is reproducible and orthogonal to
    the deterministic dynamics.
    """

    def __init__(
        self,
        rule: int,
        n_steps: int,
        p_noise: float,
        width: int = _DEFAULT_WIDTH,
        seed: int = 0,
    ) -> None:
        if not 0.0 <= p_noise <= 1.0:
            raise ValueError(f"p_noise must be in [0, 1], got {p_noise}")
        self._base = ECASystem(rule=rule, n_steps=n_steps, width=width, seed=seed)
        self._p_noise = float(p_noise)
        self._noise_rng = np.random.default_rng(seed + _NOISE_SEED_OFFSET)
        self._state_history: np.ndarray | None = None
        self._env_history: np.ndarray | None = None

    def _build(self) -> None:
        clean_states = self._base.get_state_history()
        env = self._base.get_env_history()
        flips = self._noise_rng.random(clean_states.shape[0]) < self._p_noise
        noisy = np.where(flips, 1 - clean_states, clean_states).astype(np.int64)
        self._state_history = noisy
        self._env_history = env

    def get_state_history(self) -> np.ndarray:
        if self._state_history is None:
            self._build()
        assert self._state_history is not None
        return self._state_history.copy()

    def get_env_history(self) -> np.ndarray:
        if self._env_history is None:
            self._build()
        assert self._env_history is not None
        return self._env_history.copy()


def _truncate(text: str, length: int = 80) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= length:
        return cleaned
    return cleaned[: length - 3] + "..."


def measure_safe(
    meter: Autonometer, system: NoisyECA
) -> tuple[float | None, float | None, str]:
    """Run ``meter.measure`` and turn ``ValueError`` into a recorded note."""
    try:
        profile = meter.measure(system)
    except ValueError as exc:
        return None, None, _truncate(str(exc))
    return profile.ratio_endo_total, profile.memory_endo_ratio, ""


def iter_configs(
    rule: int,
    noise_levels: tuple[float, ...],
    n_seeds: int,
    n_steps: int,
    width: int,
) -> Iterator[tuple[int, float, int, NoisyECA]]:
    """Yield ``(rule, p_noise, seed, system)`` tuples for the sweep."""
    for p in noise_levels:
        for seed in range(n_seeds):
            yield rule, p, seed, NoisyECA(
                rule=rule,
                n_steps=n_steps,
                p_noise=p,
                width=width,
                seed=seed,
            )


def run_sweep(
    rule: int = _DEFAULT_RULE,
    noise_levels: tuple[float, ...] = _DEFAULT_NOISE_LEVELS,
    n_seeds: int = _DEFAULT_N_SEEDS,
    n_steps: int = _DEFAULT_N_STEPS,
    width: int = _DEFAULT_WIDTH,
) -> list[SaturationPoint]:
    """Sweep ``noise_levels`` against ``n_seeds`` and collect points."""
    meter = Autonometer(metrics=["albantakis", "memory"])
    points: list[SaturationPoint] = []
    for rule_id, p, seed, system in iter_configs(rule, noise_levels, n_seeds, n_steps, width):
        closure, memory, notes = measure_safe(meter, system)
        points.append(
            SaturationPoint(
                rule=rule_id,
                p_noise=p,
                seed=seed,
                closure=closure,
                memory=memory,
                notes=notes,
            )
        )
    return points


def print_table(points: list[SaturationPoint]) -> None:
    """Pretty-print one row per measurement."""
    fmt = "{:>4} {:>8} {:>4} {:>10} {:>10} {}"
    print(fmt.format("rule", "p_noise", "seed", "closure", "memory", "notes"))
    print(fmt.format("-" * 4, "-" * 8, "----", "-" * 10, "-" * 10, "-" * 30))
    for p in points:
        c = "n/a" if p.closure is None else f"{p.closure:.4f}"
        m = "n/a" if p.memory is None else f"{p.memory:.4f}"
        print(fmt.format(p.rule, f"{p.p_noise:.3f}", p.seed, c, m, p.notes))


_CSV_FIELDS = ["rule", "p_noise", "seed", "closure", "memory", "notes"]


def write_csv(points: list[SaturationPoint], path: Path) -> None:
    """Persist the saturation points to ``path`` as a UTF-8 CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        for p in points:
            row = asdict(p)
            row["p_noise"] = f"{row['p_noise']:.4f}"
            row["closure"] = "" if row["closure"] is None else f"{row['closure']:.6f}"
            row["memory"] = "" if row["memory"] is None else f"{row['memory']:.6f}"
            writer.writerow(row)


def aggregate(points: list[SaturationPoint]) -> dict[float, dict[str, Any]]:
    """Reduce per-seed measurements to mean / std per noise level."""
    by_p: dict[float, list[SaturationPoint]] = {}
    for p in points:
        by_p.setdefault(p.p_noise, []).append(p)

    out: dict[float, dict[str, Any]] = {}
    for p_value, group in sorted(by_p.items()):
        valid = [g for g in group if g.closure is not None and g.memory is not None]
        if valid:
            closures = np.array([g.closure for g in valid], dtype=float)
            memories = np.array([g.memory for g in valid], dtype=float)
            out[p_value] = {
                "n_total": len(group),
                "n_valid": len(valid),
                "closure_mean": float(np.mean(closures)),
                "closure_std": float(np.std(closures)),
                "memory_mean": float(np.mean(memories)),
                "memory_std": float(np.std(memories)),
            }
        else:
            out[p_value] = {
                "n_total": len(group),
                "n_valid": 0,
                "closure_mean": float("nan"),
                "closure_std": float("nan"),
                "memory_mean": float("nan"),
                "memory_std": float("nan"),
            }
    return out


def print_aggregate(stats: dict[float, dict[str, Any]]) -> None:
    """Pretty-print the per-noise aggregate stats."""
    print()
    print("Aggregate (mean +/- std per noise level):")
    fmt = "{:>8} {:>5} {:>20} {:>20}"
    print(fmt.format("p_noise", "n", "closure", "memory"))
    print(fmt.format("-" * 8, "-" * 5, "-" * 20, "-" * 20))
    for p_value, row in stats.items():
        if row["n_valid"] == 0:
            c_str = "n/a"
            m_str = "n/a"
        else:
            c_str = f"{row['closure_mean']:.4f} +/- {row['closure_std']:.4f}"
            m_str = f"{row['memory_mean']:.4f} +/- {row['memory_std']:.4f}"
        print(fmt.format(f"{p_value:.3f}", f"{row['n_valid']}/{row['n_total']}", c_str, m_str))


def diagnosis_line(stats: dict[float, dict[str, Any]]) -> str:
    """Return a single-line verdict on whether the curve looks monotonic."""
    p_values = sorted(stats.keys())
    closures = [stats[p]["closure_mean"] for p in p_values]
    valid = [(p, c) for p, c in zip(p_values, closures, strict=True) if not np.isnan(c)]
    if len(valid) < 2:
        return "[N/A] not enough valid noise levels to assess monotonicity."

    first_p, first_c = valid[0]
    last_p, last_c = valid[-1]
    drop = first_c - last_c

    monotonic = all(
        valid[i][1] >= valid[i + 1][1] - 1e-3 for i in range(len(valid) - 1)
    )

    if drop > 0.5 and monotonic:
        return (
            f"[OK] closure({first_p:.2f}) = {first_c:.3f} -> closure({last_p:.2f}) "
            f"= {last_c:.3f}; drop = {drop:.3f}, monotone within tolerance. "
            "The saturation wall is a property of determinism + full observability, "
            "as predicted; injected noise pulls closure off the wall smoothly."
        )
    if drop > 0.2:
        return (
            f"[PARTIAL] closure drops from {first_c:.3f} to {last_c:.3f} but the "
            "curve is not strictly monotone within the tested seeds. The saturation "
            "is sensitive to noise but with non-monotone substructure worth "
            "inspecting per-seed."
        )
    return (
        f"[UNEXPECTED] closure barely moved: {first_c:.3f} -> {last_c:.3f}. "
        "The saturation is more robust to bit-flip noise than the theoretical "
        "argument predicts; this is a finding that deserves follow-up."
    )


_DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent.parent / "docs" / "benchmarks" / "saturation_v0.5.1.csv"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the autonometrics saturation diagnostic."
    )
    default_rel = _DEFAULT_OUTPUT.relative_to(_DEFAULT_OUTPUT.parents[2])
    parser.add_argument(
        "--output",
        type=Path,
        default=_DEFAULT_OUTPUT,
        help=f"CSV output path (default: {default_rel}).",
    )
    parser.add_argument(
        "--rule",
        type=int,
        default=_DEFAULT_RULE,
        help=f"ECA rule number to test (default: {_DEFAULT_RULE}).",
    )
    parser.add_argument(
        "--n-seeds",
        type=int,
        default=_DEFAULT_N_SEEDS,
        help=f"Independent seeds per noise level (default: {_DEFAULT_N_SEEDS}).",
    )
    parser.add_argument(
        "--n-steps",
        type=int,
        default=_DEFAULT_N_STEPS,
        help=f"Trajectory length (default: {_DEFAULT_N_STEPS}).",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=_DEFAULT_WIDTH,
        help=f"ECA grid width (default: {_DEFAULT_WIDTH}).",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run a tiny subset (smoke mode).",
    )
    args = parser.parse_args(argv)

    if args.quick:
        noise_levels = _QUICK_NOISE_LEVELS
        n_seeds = _QUICK_N_SEEDS
    else:
        noise_levels = _DEFAULT_NOISE_LEVELS
        n_seeds = args.n_seeds

    points = run_sweep(
        rule=args.rule,
        noise_levels=noise_levels,
        n_seeds=n_seeds,
        n_steps=args.n_steps,
        width=args.width,
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
