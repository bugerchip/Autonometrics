"""Render a constraint-vs-density curve from a constraint-density diagnostic CSV.

Reads a CSV produced by ``examples/constraint_density_diagnostic.py``
and writes a single-figure PNG showing how the constraint-closure
score reacts to connection density on a Kauffman zoo. The curve is
plotted as ``mean +/- std`` across the seeds present at each value
of ``K``.

This script depends on :mod:`matplotlib`, which is **not** a runtime
dependency of ``autonometrics``. Install the optional extra to use
it::

    pip install autonometrics[viz]

Usage::

    python examples/constraint_density_plot.py
    python examples/constraint_density_plot.py --csv path/to/run.csv \\
        --output path/to/fig.png
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import numpy as np


def load_csv(path: Path) -> list[dict[str, Any]]:
    """Load the constraint-density CSV; coerce numeric columns."""
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            row["n_nodes"] = int(row["n_nodes"])
            row["k"] = int(row["k"])
            row["seed"] = int(row["seed"])
            value = row.get("constraint", "")
            row["constraint"] = float(value) if value not in ("", None) else None
            rows.append(row)
    return rows


def aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Reduce per-seed rows to mean / std per ``K``."""
    by_k: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        by_k.setdefault(row["k"], []).append(row)

    out: list[dict[str, Any]] = []
    for k_value in sorted(by_k):
        group = by_k[k_value]
        valid = [g for g in group if g["constraint"] is not None]
        if valid:
            scores = np.array([g["constraint"] for g in valid], dtype=float)
            out.append(
                {
                    "k": k_value,
                    "n_valid": len(valid),
                    "constraint_mean": float(np.mean(scores)),
                    "constraint_std": float(np.std(scores)),
                }
            )
        else:
            out.append(
                {
                    "k": k_value,
                    "n_valid": 0,
                    "constraint_mean": float("nan"),
                    "constraint_std": float("nan"),
                }
            )
    return out


def _summary_title(rows: list[dict[str, Any]], aggregated: list[dict[str, Any]]) -> str:
    """Build a one-line title summarising the run."""
    n_set = {row["n_nodes"] for row in rows}
    n_str = (
        f"n={next(iter(n_set))}"
        if len(n_set) == 1
        else "n=" + "{" + ",".join(map(str, sorted(n_set))) + "}"
    )
    valid_levels = [a for a in aggregated if a["n_valid"] > 0]
    if valid_levels:
        first = valid_levels[0]
        last = valid_levels[-1]
        return (
            f"constraint-density diagnostic - Kauffman {n_str} - "
            f"constraint(K={first['k']})={first['constraint_mean']:.3f} "
            f"-> constraint(K={last['k']})={last['constraint_mean']:.3f}"
        )
    return f"constraint-density diagnostic - Kauffman {n_str} - no valid points"


def render(rows: list[dict[str, Any]], output: Path, title: str | None = None) -> None:
    """Render the constraint curve and write a PNG to ``output``."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError(
            "matplotlib is required to render constraint-density plots. "
            "Install with: pip install autonometrics[viz]"
        ) from exc

    aggregated = aggregate(rows)
    valid = [a for a in aggregated if a["n_valid"] > 0]
    if not valid:
        raise ValueError("CSV contains no valid constraint-closure measurements to plot.")

    k_values = np.array([a["k"] for a in valid], dtype=float)
    constraint_mean = np.array([a["constraint_mean"] for a in valid], dtype=float)
    constraint_std = np.array([a["constraint_std"] for a in valid], dtype=float)

    fig, ax = plt.subplots(figsize=(7.5, 5.5), dpi=150)

    ax.errorbar(
        k_values,
        constraint_mean,
        yerr=constraint_std,
        marker="o",
        markersize=6,
        linewidth=2.0,
        capsize=3,
        label=f"constraint_closure (n={valid[0]['n_valid']} per K)",
        color="tab:green",
    )

    ax.axhline(1.0, color="lightgray", linestyle=":", linewidth=1.0, alpha=0.7)
    ax.axhline(0.0, color="lightgray", linestyle=":", linewidth=1.0, alpha=0.7)

    ax.set_xlim(min(k_values) - 0.3, max(k_values) + 0.3)
    ax.set_ylim(-0.05, 1.08)
    ax.set_xlabel("Kauffman input degree K (upper bound on in-degree per node)")
    ax.set_ylabel("constraint_closure")
    if title is None:
        title = _summary_title(rows, aggregated)
    ax.set_title(title, fontsize=11)
    ax.legend(loc="best", framealpha=0.95, fontsize=9)
    ax.grid(True, alpha=0.25)

    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output)
    plt.close(fig)


_DEFAULT_CSV = (
    Path(__file__).resolve().parent.parent / "docs" / "benchmarks" / "constraint_density_v0.6.1.csv"
)
_DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent.parent / "docs" / "benchmarks" / "constraint_density_v0.6.1.png"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render the constraint-density diagnostic curve.")
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
