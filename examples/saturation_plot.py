"""Render a closure-vs-noise curve from a saturation diagnostic CSV.

Reads a CSV produced by ``examples/saturation_diagnostic.py`` and
writes a single-figure PNG showing how the Albantakis closure score
reacts to injected observation noise on a known-saturating system
(by default, elementary cellular automaton rule 110). The curve is
plotted as mean ± std across the seeds present at each noise level.

This script depends on :mod:`matplotlib`, which is **not** a runtime
dependency of ``autonometrics``. Install the optional extra to use
it::

    pip install autonometrics[viz]

Usage::

    python examples/saturation_plot.py
    python examples/saturation_plot.py --csv path/to/run.csv \\
        --output path/to/fig.png
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import numpy as np


def load_csv(path: Path) -> list[dict[str, Any]]:
    """Load the saturation CSV; coerce numeric columns."""
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            row["rule"] = int(row["rule"])
            row["seed"] = int(row["seed"])
            row["p_noise"] = float(row["p_noise"])
            for key in ("closure", "memory"):
                value = row.get(key, "")
                row[key] = float(value) if value not in ("", None) else None
            rows.append(row)
    return rows


def aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Reduce per-seed rows to mean / std per noise level."""
    by_p: dict[float, list[dict[str, Any]]] = {}
    for row in rows:
        by_p.setdefault(row["p_noise"], []).append(row)

    out: list[dict[str, Any]] = []
    for p_value in sorted(by_p):
        group = by_p[p_value]
        valid = [g for g in group if g["closure"] is not None and g["memory"] is not None]
        if valid:
            closures = np.array([g["closure"] for g in valid], dtype=float)
            memories = np.array([g["memory"] for g in valid], dtype=float)
            out.append(
                {
                    "p_noise": p_value,
                    "n_valid": len(valid),
                    "closure_mean": float(np.mean(closures)),
                    "closure_std": float(np.std(closures)),
                    "memory_mean": float(np.mean(memories)),
                    "memory_std": float(np.std(memories)),
                }
            )
        else:
            out.append(
                {
                    "p_noise": p_value,
                    "n_valid": 0,
                    "closure_mean": float("nan"),
                    "closure_std": float("nan"),
                    "memory_mean": float("nan"),
                    "memory_std": float("nan"),
                }
            )
    return out


def _summary_title(rows: list[dict[str, Any]], aggregated: list[dict[str, Any]]) -> str:
    """Build a one-line title summarising the run."""
    rules = {row["rule"] for row in rows}
    rule_str = "rule " + (
        f"{next(iter(rules))}" if len(rules) == 1 else "{" + ",".join(map(str, sorted(rules))) + "}"
    )
    valid_levels = [a for a in aggregated if a["n_valid"] > 0]
    if valid_levels:
        first = valid_levels[0]
        last = valid_levels[-1]
        return (
            f"saturation diagnostic - ECA {rule_str} - "
            f"closure({first['p_noise']:.2f})={first['closure_mean']:.3f} "
            f"-> closure({last['p_noise']:.2f})={last['closure_mean']:.3f}"
        )
    return f"saturation diagnostic - ECA {rule_str} - no valid points"


def render(rows: list[dict[str, Any]], output: Path, title: str | None = None) -> None:
    """Render the closure / memory curves and write a PNG to ``output``."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError(
            "matplotlib is required to render saturation plots. "
            "Install with: pip install autonometrics[viz]"
        ) from exc

    aggregated = aggregate(rows)
    valid = [a for a in aggregated if a["n_valid"] > 0]
    if not valid:
        raise ValueError("CSV contains no valid (closure, memory) measurements to plot.")

    p_values = np.array([a["p_noise"] for a in valid], dtype=float)
    closure_mean = np.array([a["closure_mean"] for a in valid], dtype=float)
    closure_std = np.array([a["closure_std"] for a in valid], dtype=float)
    memory_mean = np.array([a["memory_mean"] for a in valid], dtype=float)
    memory_std = np.array([a["memory_std"] for a in valid], dtype=float)

    fig, ax = plt.subplots(figsize=(7.5, 5.5), dpi=150)

    ax.errorbar(
        p_values,
        closure_mean,
        yerr=closure_std,
        marker="o",
        markersize=6,
        linewidth=2.0,
        capsize=3,
        label=f"closure (n={valid[0]['n_valid']} per p)",
        color="tab:blue",
    )
    ax.errorbar(
        p_values,
        memory_mean,
        yerr=memory_std,
        marker="s",
        markersize=6,
        linewidth=2.0,
        capsize=3,
        label=f"memory (n={valid[0]['n_valid']} per p)",
        color="tab:orange",
        alpha=0.7,
    )

    ax.axhline(1.0, color="lightgray", linestyle=":", linewidth=1.0, alpha=0.7)
    ax.axhline(0.0, color="lightgray", linestyle=":", linewidth=1.0, alpha=0.7)

    ax.set_xlim(-0.02, max(p_values) + 0.02)
    ax.set_ylim(-0.05, 1.08)
    ax.set_xlabel("bit-flip noise probability p")
    ax.set_ylabel("metric value")
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
    Path(__file__).resolve().parent.parent / "docs" / "benchmarks" / "saturation_v0.5.1.csv"
)
_DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent.parent / "docs" / "benchmarks" / "saturation_v0.5.1.png"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render the saturation diagnostic curve.")
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
