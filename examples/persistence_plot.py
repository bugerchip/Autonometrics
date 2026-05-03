"""Render a persistence-vs-coupling curve from a persistence diagnostic CSV.

Reads a CSV produced by ``examples/persistence_diagnostic.py`` and
writes a single-figure PNG showing how the persistence score reacts
to focal coupling on a Kauffman zoo. The curve is plotted as
``mean +/- std`` across the seeds present at each value of
``coupling``.

This script depends on :mod:`matplotlib`, which is **not** a runtime
dependency of ``autonometrics``. Install the optional extra to use
it::

    pip install autonometrics[viz]

Usage::

    python examples/persistence_plot.py
    python examples/persistence_plot.py --csv path/to/run.csv \\
        --output path/to/fig.png
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import numpy as np


def load_csv(path: Path) -> list[dict[str, Any]]:
    """Load the persistence diagnostic CSV; coerce numeric columns."""
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            row["coupling"] = float(row["coupling"])
            row["seed"] = int(row["seed"])
            value = row.get("persistence", "")
            row["persistence"] = float(value) if value not in ("", None) else None
            rows.append(row)
    return rows


def aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Reduce per-seed rows to mean / std per coupling level."""
    by_c: dict[float, list[dict[str, Any]]] = {}
    for row in rows:
        by_c.setdefault(row["coupling"], []).append(row)

    out: list[dict[str, Any]] = []
    for c_value in sorted(by_c):
        group = by_c[c_value]
        valid = [g for g in group if g["persistence"] is not None]
        if valid:
            scores = np.array([g["persistence"] for g in valid], dtype=float)
            out.append(
                {
                    "coupling": c_value,
                    "n_valid": len(valid),
                    "persistence_mean": float(np.mean(scores)),
                    "persistence_std": float(np.std(scores)),
                }
            )
        else:
            out.append(
                {
                    "coupling": c_value,
                    "n_valid": 0,
                    "persistence_mean": float("nan"),
                    "persistence_std": float("nan"),
                }
            )
    return out


def _summary_title(aggregated: list[dict[str, Any]]) -> str:
    """Build a one-line title summarising the run."""
    valid_levels = [a for a in aggregated if a["n_valid"] > 0]
    if valid_levels:
        first = valid_levels[0]
        last = valid_levels[-1]
        return (
            "persistence diagnostic - Kauffman focal coupling sweep - "
            f"persistence({first['coupling']:.2f})={first['persistence_mean']:.3f} "
            f"-> persistence({last['coupling']:.2f})={last['persistence_mean']:.3f}"
        )
    return "persistence diagnostic - no valid points"


def render(rows: list[dict[str, Any]], output: Path, title: str | None = None) -> None:
    """Render the persistence curve and write a PNG to ``output``."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError(
            "matplotlib is required to render persistence plots. "
            "Install with: pip install autonometrics[viz]"
        ) from exc

    aggregated = aggregate(rows)
    valid = [a for a in aggregated if a["n_valid"] > 0]
    if not valid:
        raise ValueError(
            "CSV contains no valid persistence measurements to plot."
        )

    couplings = np.array([a["coupling"] for a in valid], dtype=float)
    persistence_mean = np.array([a["persistence_mean"] for a in valid], dtype=float)
    persistence_std = np.array([a["persistence_std"] for a in valid], dtype=float)

    fig, ax = plt.subplots(figsize=(7.5, 5.5), dpi=150)

    ax.errorbar(
        couplings,
        persistence_mean,
        yerr=persistence_std,
        marker="o",
        markersize=6,
        linewidth=2.0,
        capsize=3,
        label=f"persistence (n={valid[0]['n_valid']} per coupling)",
        color="tab:purple",
    )

    ax.axhline(1.0, color="lightgray", linestyle=":", linewidth=1.0, alpha=0.7)
    ax.axhline(0.0, color="lightgray", linestyle=":", linewidth=1.0, alpha=0.7)

    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.08)
    ax.set_xlabel("Kauffman focal coupling (0 = self-only, 1 = external-only)")
    ax.set_ylabel("rai_proxy_persistence")
    if title is None:
        title = _summary_title(aggregated)
    ax.set_title(title, fontsize=11)
    ax.legend(loc="best", framealpha=0.95, fontsize=9)
    ax.grid(True, alpha=0.25)

    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output)
    plt.close(fig)


_DEFAULT_CSV = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "benchmarks"
    / "persistence_v0.7.0.csv"
)
_DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "benchmarks"
    / "persistence_v0.7.0.png"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render the persistence diagnostic curve."
    )
    csv_rel = _DEFAULT_CSV.relative_to(_DEFAULT_CSV.parents[2])
    out_rel = _DEFAULT_OUTPUT.relative_to(_DEFAULT_OUTPUT.parents[2])
    parser.add_argument(
        "--csv",
        type=Path,
        default=_DEFAULT_CSV,
        help=f"Input CSV (default: {csv_rel}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=_DEFAULT_OUTPUT,
        help=f"Output PNG (default: {out_rel}).",
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Override the auto-generated title.",
    )
    args = parser.parse_args(argv)

    if not args.csv.is_file():
        parser.error(f"CSV not found: {args.csv}")

    rows = load_csv(args.csv)
    render(rows, args.output, title=args.title)
    print(f"Figure saved to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
