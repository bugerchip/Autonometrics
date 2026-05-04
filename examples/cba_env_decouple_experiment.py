"""Causal test of the closure × coherence artefact (Idea 1, v0.8.0a0).

The audit in ``examples/cba_independence_audit.py`` showed the
headline ``r(closure, coherence) = +0.96`` in PromisedCycle was
driven by a single shared driver — ``p_noise`` — and that
within-cell correlations decay smoothly down to ``≈ 0``. That is
**correlational** evidence for the artefact hypothesis. This
script provides **causal** evidence by introducing a second,
statistically independent driver of variability — ``p_env`` —
and rerunning the same correlation analysis on the new
two-driver design.

Hypothesis to falsify
---------------------
If the closure × coherence coupling is structural, adding a
second independent driver should leave the correlation
essentially unchanged (the structure persists no matter how the
two are wiggled). If the coupling is an adapter artefact, the
global correlation should drop substantially because each
metric now responds to its own dominant axis: closure tracks
total executed-trajectory entropy (responsive to both p_noise
and p_env), while coherence tracks ``I(D;E)/H(D)`` whose
conditional entropy depends only on p_noise.

The test is causal because we **change the data-generating
process** (a knob the experimenter controls) and observe the
effect on the correlation. This is stronger than reweighting
existing data.

Design
------
A two-axis sweep ``(p_noise, p_env)`` on ``PromisedCycle`` for a
fixed ``(period, alphabet, length)`` and ``n_seeds`` repeats per
cell. Closure and coherence are measured at every point.
Outputs:

- console summary table,
- structured JSON snapshot with global, single-axis and
  cell-level correlations,
- a 2D scatter PNG colouring closure × coherence by ``p_env`` and
  shaping by ``p_noise`` (matplotlib optional).

Default parameters keep the run small (~hundreds of points),
fast (under a minute) and self-contained: the script does not
read or modify the main benchmark CSV.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from autonometrics.adapters import PromisedCycle
from autonometrics.core import Autonometer


_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_JSON = _REPO_ROOT / "docs" / "benchmarks" / "cba_env_decouple_v0.8.0a0.json"
_DEFAULT_PNG = _REPO_ROOT / "docs" / "benchmarks" / "cba_env_decouple_v0.8.0a0.png"


@dataclass
class Cell:
    """One ``(p_noise, p_env, seed)`` measurement."""

    p_noise: float
    p_env: float
    seed: int
    closure: float | None
    coherence: float | None


def measure_cell(
    *,
    period: int,
    alphabet: int,
    length: int,
    p_noise: float,
    p_env: float,
    seed: int,
    metrics: tuple[str, ...] = ("albantakis", "coherence"),
) -> Cell:
    sys = PromisedCycle(
        length=length,
        period=period,
        alphabet=alphabet,
        p_noise=p_noise,
        p_env=p_env,
        seed=seed,
    )
    measurer = Autonometer(metrics=metrics)
    profile = measurer.measure(sys)
    return Cell(
        p_noise=p_noise,
        p_env=p_env,
        seed=seed,
        closure=profile.ratio_endo_total,
        coherence=profile.cba_theil_u,
    )


def run_sweep(
    *,
    period: int = 4,
    alphabet: int = 4,
    length: int = 4000,
    p_noise_values: tuple[float, ...] = (0.1, 0.3, 0.5, 0.7, 0.9),
    p_env_values: tuple[float, ...] = (0.0, 0.25, 0.5, 0.75, 1.0),
    n_seeds: int = 8,
) -> list[Cell]:
    cells: list[Cell] = []
    for p_noise in p_noise_values:
        for p_env in p_env_values:
            for seed in range(n_seeds):
                cells.append(
                    measure_cell(
                        period=period,
                        alphabet=alphabet,
                        length=length,
                        p_noise=p_noise,
                        p_env=p_env,
                        seed=seed,
                    )
                )
    return cells


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 2:
        return float("nan")
    if np.std(x) <= 0 or np.std(y) <= 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def _valid_pair(cells: list[Cell]) -> tuple[np.ndarray, np.ndarray]:
    xs = [
        c.closure for c in cells
        if c.closure is not None and c.coherence is not None
    ]
    ys = [
        c.coherence for c in cells
        if c.closure is not None and c.coherence is not None
    ]
    return np.asarray(xs, dtype=float), np.asarray(ys, dtype=float)


def analyse(cells: list[Cell]) -> dict[str, Any]:
    """Return global and conditional correlation summaries."""
    xs, ys = _valid_pair(cells)
    n_total = int(xs.size)

    p_env_values = sorted({c.p_env for c in cells})
    p_noise_values = sorted({c.p_noise for c in cells})

    by_p_env: dict[float, dict[str, Any]] = {}
    for p in p_env_values:
        sub = [c for c in cells if c.p_env == p]
        sx, sy = _valid_pair(sub)
        by_p_env[p] = {
            "n": int(sx.size),
            "pearson": pearson(sx, sy),
        }

    by_p_noise: dict[float, dict[str, Any]] = {}
    for q in p_noise_values:
        sub = [c for c in cells if c.p_noise == q]
        sx, sy = _valid_pair(sub)
        by_p_noise[q] = {
            "n": int(sx.size),
            "pearson": pearson(sx, sy),
        }

    by_cell: list[dict[str, Any]] = []
    for q in p_noise_values:
        for p in p_env_values:
            sub = [c for c in cells if c.p_env == p and c.p_noise == q]
            sx, sy = _valid_pair(sub)
            by_cell.append(
                {
                    "p_noise": q,
                    "p_env": p,
                    "n": int(sx.size),
                    "mean_closure": float(np.mean(sx)) if sx.size else float("nan"),
                    "mean_coherence": float(np.mean(sy)) if sy.size else float("nan"),
                    "pearson": pearson(sx, sy),
                }
            )

    p_noise_arr = np.array(
        [c.p_noise for c in cells if c.closure is not None and c.coherence is not None]
    )
    p_env_arr = np.array(
        [c.p_env for c in cells if c.closure is not None and c.coherence is not None]
    )

    return {
        "n_total": n_total,
        "global_pearson": pearson(xs, ys),
        "closure_vs_p_noise_pearson": pearson(xs, p_noise_arr),
        "closure_vs_p_env_pearson": pearson(xs, p_env_arr),
        "coherence_vs_p_noise_pearson": pearson(ys, p_noise_arr),
        "coherence_vs_p_env_pearson": pearson(ys, p_env_arr),
        "fixed_p_env_correlations": {f"{k:.3f}": v for k, v in by_p_env.items()},
        "fixed_p_noise_correlations": {f"{k:.3f}": v for k, v in by_p_noise.items()},
        "cell_correlations": by_cell,
    }


def _fmt(value: float | None) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "  n/a"
    return f"{value:+.4f}"


def print_report(result: dict[str, Any]) -> None:
    print("CBA × closure causal decouple experiment (v0.8.0a0)")
    print("=" * 68)
    print()
    print(f"Total measurements: {result['n_total']}")
    print()
    print(f"  global r(closure, coherence)             = {_fmt(result['global_pearson'])}")
    print(f"  r(closure, p_noise)                      = {_fmt(result['closure_vs_p_noise_pearson'])}")
    print(f"  r(closure, p_env)                        = {_fmt(result['closure_vs_p_env_pearson'])}")
    print(f"  r(coherence, p_noise)                    = {_fmt(result['coherence_vs_p_noise_pearson'])}")
    print(f"  r(coherence, p_env)                      = {_fmt(result['coherence_vs_p_env_pearson'])}")
    print()
    print("--- r(closure, coherence) at fixed p_env ---")
    print(f"  {'p_env':>8} {'n':>5} {'pearson':>10}")
    print(f"  {'-' * 8} {'-' * 5} {'-' * 10}")
    for k, stats in result["fixed_p_env_correlations"].items():
        print(f"  {float(k):>8.3f} {stats['n']:>5} {_fmt(stats['pearson']):>10}")
    print()
    print("--- r(closure, coherence) at fixed p_noise ---")
    print(f"  {'p_noise':>8} {'n':>5} {'pearson':>10}")
    print(f"  {'-' * 8} {'-' * 5} {'-' * 10}")
    for k, stats in result["fixed_p_noise_correlations"].items():
        print(f"  {float(k):>8.3f} {stats['n']:>5} {_fmt(stats['pearson']):>10}")
    print()
    print("--- per-cell mean(closure) and mean(coherence) ---")
    print(
        f"  {'p_noise':>8} {'p_env':>6} {'n':>4} "
        f"{'mean_clos':>10} {'mean_coh':>10} {'r':>9}"
    )
    print(f"  {'-' * 8} {'-' * 6} {'-' * 4} {'-' * 10} {'-' * 10} {'-' * 9}")
    for cell in result["cell_correlations"]:
        print(
            f"  {cell['p_noise']:>8.3f} {cell['p_env']:>6.3f} "
            f"{cell['n']:>4} "
            f"{_fmt(cell['mean_closure']):>10} "
            f"{_fmt(cell['mean_coherence']):>10} "
            f"{_fmt(cell['pearson']):>9}"
        )
    print()
    print("Interpretation rule (decided pre-run):")
    print("  - If global r drops to |r| < 0.9 (the hard gate), the artefact")
    print("    hypothesis is causally supported: the +0.96 in the v0.8.0a0")
    print("    benchmark was due to PromisedCycle having a single driver.")
    print("  - If global r stays >= 0.9, the structural-coupling hypothesis")
    print("    is reinforced and the hard gate stands.")


def write_json(result: dict[str, Any], cells: list[Cell], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    def _convert(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {str(k): _convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_convert(v) for v in obj]
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, float) and np.isnan(obj):
            return None
        return obj

    payload = {
        "summary": _convert(result),
        "raw_cells": [
            {
                "p_noise": c.p_noise,
                "p_env": c.p_env,
                "seed": c.seed,
                "closure": c.closure,
                "coherence": c.coherence,
            }
            for c in cells
        ],
    }
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)


_NOISE_MARKERS = ("o", "s", "^", "D", "v", "P", "X", "*", "<", ">")


def write_scatter(cells: list[Cell], path: Path) -> bool:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    p_noise_values = sorted({c.p_noise for c in cells})

    fig, ax = plt.subplots(figsize=(8.0, 6.5))
    sc = None
    for i, p_noise in enumerate(p_noise_values):
        sub = [
            c for c in cells
            if c.p_noise == p_noise
            and c.closure is not None
            and c.coherence is not None
        ]
        if not sub:
            continue
        x = np.array([c.closure for c in sub], dtype=float)
        y = np.array([c.coherence for c in sub], dtype=float)
        z = np.array([c.p_env for c in sub], dtype=float)
        marker = _NOISE_MARKERS[i % len(_NOISE_MARKERS)]
        sc = ax.scatter(
            x, y, c=z, cmap="plasma", marker=marker, s=44,
            label=f"p_noise={p_noise:.2f}", edgecolors="black", linewidths=0.3,
            alpha=0.85, vmin=0.0, vmax=1.0,
        )

    if sc is not None:
        cbar = fig.colorbar(sc, ax=ax)
        cbar.set_label("p_env (declared-channel noise)")

    ax.plot([0, 1], [0, 1], color="grey", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.set_xlabel("closure (ratio_endo_total)")
    ax.set_ylabel("coherence (cba_theil_u)")
    ax.set_title(
        "PromisedCycle: closure × coherence under two-driver sweep\n"
        "(causal test of the |r|=0.96 artefact)"
    )
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", fontsize=8, ncol=2, framealpha=0.9)

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Causal closure × coherence decouple experiment for autonometrics."
    )
    parser.add_argument("--period", type=int, default=4)
    parser.add_argument("--alphabet", type=int, default=4)
    parser.add_argument("--length", type=int, default=4000)
    parser.add_argument("--n-seeds", type=int, default=8)
    parser.add_argument("--json-output", type=Path, default=_DEFAULT_JSON)
    parser.add_argument("--png-output", type=Path, default=_DEFAULT_PNG)
    parser.add_argument(
        "--quick", action="store_true",
        help="Run a 3 × 3 grid with 3 seeds (smoke-fast).",
    )
    parser.add_argument(
        "--no-plot", action="store_true", help="Skip the scatter PNG output."
    )
    args = parser.parse_args(argv)

    if args.quick:
        p_noise_values = (0.2, 0.5, 0.8)
        p_env_values = (0.0, 0.5, 1.0)
        n_seeds = 3
    else:
        p_noise_values = (0.1, 0.3, 0.5, 0.7, 0.9)
        p_env_values = (0.0, 0.25, 0.5, 0.75, 1.0)
        n_seeds = args.n_seeds

    cells = run_sweep(
        period=args.period,
        alphabet=args.alphabet,
        length=args.length,
        p_noise_values=p_noise_values,
        p_env_values=p_env_values,
        n_seeds=n_seeds,
    )
    result = analyse(cells)
    print_report(result)
    write_json(result, cells, args.json_output)
    print(f"\nJSON saved to: {args.json_output}")
    if args.no_plot:
        return 0
    if write_scatter(cells, args.png_output):
        print(f"PNG saved to:  {args.png_output}")
    else:
        print("matplotlib not available; scatter PNG skipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
