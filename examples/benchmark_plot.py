"""Render a ``(closure, memory)`` scatter from a benchmark CSV.

Reads a CSV produced by ``examples/benchmark_demo.py`` and writes a
single-figure PNG to disk. Points are coloured by their system class
and the four quadrants of the autonomy plane are drawn as soft
guides. Degenerate rows (``closure`` or ``memory`` empty in the CSV)
are dropped silently — they are recorded in the CSV itself with a
``notes`` field, and the figure is meant to communicate the
distribution over the *valid* sample.

This script depends on :mod:`matplotlib`, which is **not** a runtime
dependency of ``autonometrics``. Install the optional extra to use
it::

    pip install autonometrics[viz]

Usage::

    python examples/benchmark_plot.py
    python examples/benchmark_plot.py --csv path/to/run.csv \\
        --output path/to/fig.png
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


def load_csv(path: Path) -> list[dict[str, Any]]:
    """Load a benchmark CSV; coerce ``closure``/``memory`` to ``float | None``."""
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            for key in ("closure", "memory"):
                value = row.get(key, "")
                row[key] = float(value) if value not in ("", None) else None
            row["seed"] = int(row["seed"])
            rows.append(row)
    return rows


def _summary_line(rows: list[dict[str, Any]]) -> str:
    """Build a one-line title summary from the benchmark rows."""
    valid = [r for r in rows if r["closure"] is not None and r["memory"] is not None]
    n_valid = len(valid)
    n_total = len(rows)
    if n_valid >= 2:
        c = np.array([r["closure"] for r in valid], dtype=float)
        m = np.array([r["memory"] for r in valid], dtype=float)
        if np.std(c) > 0 and np.std(m) > 0:
            r_p = float(np.corrcoef(c, m)[0, 1])
        else:
            r_p = float("nan")
    else:
        r_p = float("nan")

    abs_r = abs(r_p) if not np.isnan(r_p) else float("nan")
    if np.isnan(abs_r):
        flag = "N/A"
    elif abs_r < 0.7:
        flag = "OK"
    elif abs_r < 0.9:
        flag = "WARN"
    else:
        flag = "FAIL"

    return f"autonometrics benchmark - n={n_valid}/{n_total} valid - Pearson r={r_p:+.2f} ({flag})"


def _classify(row: dict[str, Any]) -> tuple[str, str | None]:
    """Return ``(class, sub_label)``; only ``SimpleAutomaton`` carries a sub-label."""
    if row["class"] == "SimpleAutomaton":
        return row["class"], str(row["params"])
    return row["class"], None


def _marker_for(sub: str | None) -> str:
    """Pick a marker shape; ``external`` runs are crosses, everything else circles."""
    if sub == "external":
        return "x"
    return "o"


def _label_for(klass: str, sub: str | None, n: int) -> str:
    """Build a legend label for a ``(class, sub)`` group."""
    if sub is None:
        return f"{klass} (n={n})"
    return f"{klass} [{sub}] (n={n})"


def render(rows: list[dict[str, Any]], output: Path, title: str | None = None) -> None:
    """Render the scatter and write a PNG to ``output``.

    Importing :mod:`matplotlib` is deferred to call-time so the rest
    of the module can be imported (and unit-tested) without the
    optional dependency.
    """
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError(
            "matplotlib is required to render benchmark plots. "
            "Install with: pip install autonometrics[viz]"
        ) from exc

    fig, ax = plt.subplots(figsize=(7.0, 6.5), dpi=150)

    by_group: dict[tuple[str, str | None], list[tuple[float, float]]] = defaultdict(list)
    for r in rows:
        if r["closure"] is None or r["memory"] is None:
            continue
        by_group[_classify(r)].append((r["closure"], r["memory"]))

    palette = plt.get_cmap("tab10")
    class_to_color: dict[str, Any] = {}
    for klass, _sub in by_group:
        if klass not in class_to_color:
            class_to_color[klass] = palette(len(class_to_color))

    sorted_groups = sorted(by_group.items(), key=lambda kv: (kv[0][0], kv[0][1] or ""))
    for (klass, sub), points in sorted_groups:
        xs, ys = zip(*points, strict=True)
        marker = _marker_for(sub)
        ax.scatter(
            xs,
            ys,
            label=_label_for(klass, sub, len(points)),
            s=60,
            alpha=0.75,
            marker=marker,
            color=class_to_color[klass],
            edgecolors="black" if marker == "o" else None,
            linewidths=0.5 if marker == "o" else 1.5,
        )

    ax.axhline(0.5, color="gray", linestyle=":", linewidth=1.0, alpha=0.6)
    ax.axvline(0.5, color="gray", linestyle=":", linewidth=1.0, alpha=0.6)

    quadrant_label_kwargs = dict(color="lightgray", fontsize=10, fontweight="bold")
    ax.text(0.25, 0.97, "turbulence", ha="center", va="top", **quadrant_label_kwargs)
    ax.text(0.75, 0.97, "autopoietic", ha="center", va="top", **quadrant_label_kwargs)
    ax.text(0.25, 0.03, "drift", ha="center", va="bottom", **quadrant_label_kwargs)
    ax.text(0.75, 0.03, "clockwork", ha="center", va="bottom", **quadrant_label_kwargs)

    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel("closure (ratio_endo_total)")
    ax.set_ylabel("memory (memory_endo_ratio)")
    if title is None:
        title = _summary_line(rows)
    ax.set_title(title, fontsize=11)
    ax.legend(loc="lower left", framealpha=0.95, fontsize=8)
    ax.grid(True, alpha=0.25)

    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output)
    plt.close(fig)


_DEFAULT_CSV = (
    Path(__file__).resolve().parent.parent / "docs" / "benchmarks" / "v0.5.0a0.csv"
)
_DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent.parent / "docs" / "benchmarks" / "v0.5.0a0.png"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render the autonometrics benchmark scatter.")
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
