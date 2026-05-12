"""Render PCA biplot and scree plot for the v0.7.2a0 atlas geometry.

Reads the structured JSON output of ``examples/atlas_geometry.py``
(default: ``docs/benchmarks/atlas_geometry_v0.7.2a0.json``) and
produces a single PNG with two panels:

- **Left panel (scree plot).** Per-component variance share with
  the cumulative curve overlaid. The pre-registered PCA reading in
  ``docs/ATLAS_GEOMETRY.md`` is grounded in the height of the
  first bar and the cumulative value at PC2.
- **Right panel (biplot).** PC1 vs PC2 scatter of the standardised
  benchmark points, coloured by their k-means cluster at ``k*``,
  shape-coded by adapter class, with the four axis loadings drawn
  as labelled arrows. The biplot is the canonical PCA
  visualisation for evaluating low-dimensionality and isotropy.

The script also recomputes the PCA from the benchmark CSV (it
reads the same ``v0.7.2a0.csv`` that the analyser used) so the
biplot can place individual points; the PCA structure stored in
the JSON is reused for the loadings and the variance shares.

This script depends on :mod:`matplotlib`. Install with::

    pip install autonometrics[viz]

t-SNE / UMAP plots are deliberately **not** included. The
pre-registration (``docs/ATLAS_GEOMETRY.md``, decision 2.3) flags
them as illustrative-only and warns that they can produce
spurious clusters on isotropic noise. The PCA biplot is preferred
because it is linear, deterministic, and faithful to the
variance structure under the same standardisation as the
silhouette analysis.

Usage::

    python examples/atlas_geometry_plot.py
    python examples/atlas_geometry_plot.py --json path/to/report.json \\
        --csv path/to/run.csv --output path/to/fig.png
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import numpy as np

_AXES: tuple[str, ...] = ("closure", "memory", "constraint", "persistence")


def _load_atlas_module() -> ModuleType:
    """Import ``examples/atlas_geometry.py`` as a module by file path.

    The plotting script reuses the analyser's CSV loader, the
    standardiser, and the k-means routine to keep the cluster
    assignments perfectly consistent with the pre-registered
    JSON snapshot.
    """
    if "atlas_geometry" in sys.modules:
        return sys.modules["atlas_geometry"]
    here = Path(__file__).resolve().parent
    src_path = here / "atlas_geometry.py"
    spec = importlib.util.spec_from_file_location("atlas_geometry", src_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load atlas_geometry at {src_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["atlas_geometry"] = module
    spec.loader.exec_module(module)
    return module


def load_report(path: Path) -> dict[str, Any]:
    """Load the JSON snapshot produced by ``examples/atlas_geometry.py``."""
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _project_for_biplot(
    csv_path: Path,
    report: dict[str, Any],
    rng_seed: int = 0,
) -> dict[str, np.ndarray]:
    """Recompute PC1/PC2 scores and k-means labels for the benchmark CSV.

    Reuses the analyser's helpers so that the cluster assignment in
    the figure matches the JSON snapshot exactly (modulo cluster
    relabelling: k-means is invariant under cluster permutations).
    """
    atlas = _load_atlas_module()
    rows = atlas.load_csv(csv_path)
    valid = [r for r in rows if r.is_valid]
    matrix = np.array([r.vector for r in valid], dtype=float)
    scaled, _mean, _std = atlas.standardise(matrix)
    pca = atlas.pca_via_svd(scaled)
    k_star = int(report["kmeans"]["k_star"])
    rng = np.random.default_rng(rng_seed)
    labels, _centroids, _inertia = atlas.kmeans(pca["whitened"], k_star, rng=rng)
    classes = np.array([r.klass for r in valid])
    return {
        "scores_pc": pca["scores"][:, :2],
        "labels": labels,
        "classes": classes,
        "components": pca["components"],
        "explained_ratio": pca["explained_variance_ratio"],
    }


_CLASS_MARKER: dict[str, str] = {
    "ECASystem": "o",
    "KauffmanNetwork": "s",
    "PeriodicCycle": "^",
    "SimpleAutomaton": "D",
}


def render(
    report: dict[str, Any],
    projection: dict[str, np.ndarray],
    output: Path,
) -> None:
    """Render the two-panel figure to ``output`` as a PNG."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError(
            "matplotlib is required to render the atlas geometry plot. "
            "Install with: pip install autonometrics[viz]"
        ) from exc

    fig, (ax_scree, ax_biplot) = plt.subplots(1, 2, figsize=(13.0, 6.0), dpi=150)

    ratios = np.asarray(report["pca"]["explained_variance_ratio"], dtype=float)
    cumul = np.asarray(report["pca"]["cumulative_ratio"], dtype=float)
    components = np.array([f"PC{i + 1}" for i in range(ratios.size)])

    bars = ax_scree.bar(components, ratios, color="#4a7fb8", edgecolor="black", alpha=0.85)
    for bar, r in zip(bars, ratios, strict=False):
        ax_scree.text(
            bar.get_x() + bar.get_width() / 2,
            r + 0.01,
            f"{r:.3f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax_cumul = ax_scree.twinx()
    ax_cumul.plot(
        components,
        cumul,
        marker="o",
        color="#c4541d",
        linewidth=2.0,
        label="cumulative",
    )
    for x, c in zip(components, cumul, strict=False):
        ax_cumul.text(x, c + 0.02, f"{c:.3f}", ha="center", color="#c4541d", fontsize=8)
    ax_scree.set_ylim(0.0, 1.05)
    ax_cumul.set_ylim(0.0, 1.05)
    ax_scree.set_ylabel("variance share lambda_i")
    ax_cumul.set_ylabel("cumulative")
    ax_scree.set_title("PCA scree (z-scored 4-axis cloud)")
    ax_scree.grid(True, axis="y", alpha=0.25)

    pre_threshold = 0.70
    ax_scree.axhline(
        pre_threshold,
        color="gray",
        linestyle=":",
        linewidth=1.0,
        alpha=0.6,
    )
    ax_scree.text(
        0.02,
        pre_threshold + 0.01,
        "pre-registered lambda_1 >= 0.70 line",
        transform=ax_scree.get_yaxis_transform(),
        fontsize=7,
        color="gray",
    )

    scores = projection["scores_pc"]
    labels = projection["labels"]
    classes = projection["classes"]
    components_full = projection["components"]
    expl = projection["explained_ratio"]

    palette = plt.get_cmap("tab10")
    unique_labels = sorted(set(int(x) for x in labels))
    label_to_color = {lab: palette(i % 10) for i, lab in enumerate(unique_labels)}

    for klass in sorted(set(classes.tolist())):
        for lab in unique_labels:
            mask = (classes == klass) & (labels == lab)
            if not np.any(mask):
                continue
            ax_biplot.scatter(
                scores[mask, 0],
                scores[mask, 1],
                marker=_CLASS_MARKER.get(klass, "o"),
                color=label_to_color[lab],
                edgecolors="black",
                linewidths=0.4,
                alpha=0.8,
                s=42.0,
            )

    arrow_scale = 1.5 * float(np.max(np.abs(scores)))
    for j, axis_name in enumerate(_AXES):
        dx = components_full[0, j] * arrow_scale
        dy = components_full[1, j] * arrow_scale
        ax_biplot.arrow(
            0.0,
            0.0,
            dx,
            dy,
            head_width=0.08,
            length_includes_head=True,
            color="#222222",
            alpha=0.85,
            linewidth=1.4,
        )
        ax_biplot.text(
            dx * 1.08,
            dy * 1.08,
            axis_name,
            color="#222222",
            fontsize=9,
            fontweight="bold",
            ha="center",
            va="center",
        )

    ax_biplot.axhline(0, color="lightgray", linewidth=0.8)
    ax_biplot.axvline(0, color="lightgray", linewidth=0.8)
    ax_biplot.set_xlabel(f"PC1 ({expl[0]:.1%})")
    ax_biplot.set_ylabel(f"PC2 ({expl[1]:.1%})")
    ax_biplot.set_title(
        f"PCA biplot - n={len(scores)} valid points, "
        f"k* = {report['kmeans']['k_star']}, "
        f"s(k*) = {report['kmeans']['silhouette'][str(report['kmeans']['k_star'])]:+.3f}"
    )
    ax_biplot.grid(True, alpha=0.2)

    legend_handles: list[Any] = []
    for klass in sorted(set(classes.tolist())):
        legend_handles.append(
            plt.Line2D(
                [0],
                [0],
                marker=_CLASS_MARKER.get(klass, "o"),
                color="white",
                markerfacecolor="#888888",
                markeredgecolor="black",
                markersize=8,
                label=f"{klass}",
            )
        )
    for lab in unique_labels:
        legend_handles.append(
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color=label_to_color[lab],
                linestyle="",
                markersize=8,
                label=f"k-means cluster {lab}",
            )
        )
    ax_biplot.legend(handles=legend_handles, loc="lower right", fontsize=7, ncol=1)

    fig.suptitle(
        "Atlas geometry (autonometrics v0.7.2a0). PCA + k-means biplot. Loadings on PC1/PC2 axes.",
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output)
    plt.close(fig)


_DEFAULT_JSON = (
    Path(__file__).resolve().parent.parent / "docs" / "benchmarks" / "atlas_geometry_v0.7.2a0.json"
)
_DEFAULT_CSV = Path(__file__).resolve().parent.parent / "docs" / "benchmarks" / "v0.7.2a0.csv"
_DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent.parent / "docs" / "benchmarks" / "atlas_geometry_v0.7.2a0.png"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render the atlas geometry biplot + scree plot.")
    parser.add_argument(
        "--json",
        type=Path,
        default=_DEFAULT_JSON,
        help="Atlas geometry JSON report (default: docs/benchmarks/atlas_geometry_v0.7.2a0.json).",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=_DEFAULT_CSV,
        help="Benchmark CSV (default: docs/benchmarks/v0.7.2a0.csv).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=_DEFAULT_OUTPUT,
        help="Output PNG (default: docs/benchmarks/atlas_geometry_v0.7.2a0.png).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="RNG seed used to recompute the k-means labels (default: 0).",
    )
    args = parser.parse_args(argv)

    if not args.json.is_file():
        parser.error(f"JSON not found: {args.json}")
    if not args.csv.is_file():
        parser.error(f"CSV not found: {args.csv}")

    report = load_report(args.json)
    projection = _project_for_biplot(args.csv, report, rng_seed=args.seed)
    render(report, projection, args.output)
    print(f"Figure saved to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
