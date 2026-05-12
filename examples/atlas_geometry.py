"""Atlas geometry analysis for ``autonometrics`` v0.7.2a0.

Reads a benchmark CSV produced by ``examples/benchmark_demo.py`` and
runs the **pre-registered** geometric analysis on the
``(closure, memory, constraint, persistence)`` cloud:

1. **PCA** via :func:`numpy.linalg.svd` on the standardised
   (z-scored) data matrix. Reports per-component variance shares
   ``lambda_i`` and the cumulative ``lambda_1 + lambda_2``.
2. **K-means clustering** for ``k in {2, 3, 4, 5}`` on the
   PCA-whitened data, with the **silhouette score** (Rousseeuw 1987)
   computed on each ``k``. The chosen ``k* = argmax_k s(k)``. The
   strength of the clustering is read from the silhouette value
   itself.
3. **Adapter-class composition** of the ``k*`` clusters. Each
   cluster's contents are tabulated by the ``class`` field
   (``ECASystem`` / ``KauffmanNetwork`` / ``PeriodicCycle`` /
   ``SimpleAutomaton``); a cluster dominated by a single class is
   evidence that the clustering tracks zoo structure rather than
   autonomy structure (Level-3 reading).
4. **Conditional Pearson correlations**:
   - within each ``k*`` cluster (Simpson-paradox check),
   - within each adapter class.
   These detect the case where the global pairwise correlations
   (`docs/PBA.md`) hide stronger or weaker structure inside the
   sub-populations.
5. **Dropout pattern**: number of points dropped per adapter class
   and (where available) per parameter setting.

Outputs:

- a human-readable report on stdout,
- a structured JSON snapshot at
  ``docs/benchmarks/atlas_geometry_v0.7.2a0.json`` (overridable
  via ``--output``).

This script is intentionally numpy-only. It is a *consumer* of
``autonometrics`` (it reads only the benchmark CSV and does not
import the package) and therefore does not extend the public API,
in line with `docs/ATLAS_GEOMETRY.md`'s independence-by-design
clause.

The pre-registered thresholds for interpreting the output are
listed in `docs/ATLAS_GEOMETRY.md`. This script does **not** apply
those thresholds itself; it only computes the indicators. The
verdict step (interpretation against thresholds) is performed in
the documentation phase, not here, so the analysis code remains
threshold-free.

Usage::

    python examples/atlas_geometry.py
    python examples/atlas_geometry.py --csv path/to/run.csv \\
        --output path/to/report.json
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

_AXES: tuple[str, ...] = ("closure", "memory", "constraint", "persistence")
_PAIRS: tuple[tuple[str, str], ...] = (
    ("closure", "memory"),
    ("closure", "constraint"),
    ("closure", "persistence"),
    ("memory", "constraint"),
    ("memory", "persistence"),
    ("constraint", "persistence"),
)
_K_GRID: tuple[int, ...] = (2, 3, 4, 5)
_KMEANS_RESTARTS: int = 20
_KMEANS_MAX_ITER: int = 200
_KMEANS_TOL: float = 1e-8


@dataclass
class BenchmarkRow:
    """A single benchmark row with all four axes resolved or ``None``."""

    klass: str
    params: str
    seed: int
    closure: float | None
    memory: float | None
    constraint: float | None
    persistence: float | None
    notes: str

    @property
    def is_valid(self) -> bool:
        return all(getattr(self, name) is not None for name in _AXES)

    @property
    def vector(self) -> np.ndarray:
        return np.array([getattr(self, name) for name in _AXES], dtype=float)


def _maybe_float_field(raw: dict[str, str], name: str) -> float | None:
    value = raw.get(name, "")
    if value in ("", None):
        return None
    return float(value)


def load_csv(path: Path) -> list[BenchmarkRow]:
    """Parse a benchmark CSV into a list of :class:`BenchmarkRow`."""
    rows: list[BenchmarkRow] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            rows.append(
                BenchmarkRow(
                    klass=raw["class"],
                    params=raw["params"],
                    seed=int(raw["seed"]),
                    closure=_maybe_float_field(raw, "closure"),
                    memory=_maybe_float_field(raw, "memory"),
                    constraint=_maybe_float_field(raw, "constraint"),
                    persistence=_maybe_float_field(raw, "persistence"),
                    notes=raw.get("notes", ""),
                )
            )
    return rows


def standardise(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Z-score the columns; return ``(scaled, mean, std)``.

    Columns with zero variance are passed through unchanged but
    flagged as ``std = 1`` to avoid divide-by-zero, since z-scoring
    a constant column is undefined.
    """
    mean = matrix.mean(axis=0)
    std = matrix.std(axis=0, ddof=0)
    safe = np.where(std > 0, std, 1.0)
    return (matrix - mean) / safe, mean, safe


def pca_via_svd(scaled: np.ndarray) -> dict[str, Any]:
    """Run PCA via SVD on a standardised matrix.

    Returns:
        dict with keys ``components`` (each row is an eigenvector),
        ``explained_variance``, ``explained_variance_ratio``,
        ``cumulative_ratio``, ``scores`` (data projected on
        components), and ``whitened`` (scores divided by component
        std).
    """
    n_samples = scaled.shape[0]
    if n_samples < 2:
        raise ValueError("PCA needs at least 2 samples.")

    u, s, vt = np.linalg.svd(scaled, full_matrices=False)
    explained_var = (s**2) / (n_samples - 1)
    total = float(explained_var.sum())
    if total <= 0:
        raise ValueError("Total variance is zero; PCA is undefined.")
    explained_ratio = explained_var / total
    cumulative = np.cumsum(explained_ratio)
    scores = u * s
    whitened_scale = np.where(s > 0, s, 1.0) / np.sqrt(n_samples - 1)
    whitened = scores / whitened_scale

    return {
        "components": vt,
        "explained_variance": explained_var,
        "explained_variance_ratio": explained_ratio,
        "cumulative_ratio": cumulative,
        "scores": scores,
        "whitened": whitened,
    }


def _pairwise_distances_sq(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Squared Euclidean distance matrix between rows of ``x`` and ``y``."""
    diff = x[:, None, :] - y[None, :, :]
    return np.sum(diff * diff, axis=-1)


def kmeans(
    data: np.ndarray,
    k: int,
    *,
    n_restarts: int = _KMEANS_RESTARTS,
    max_iter: int = _KMEANS_MAX_ITER,
    tol: float = _KMEANS_TOL,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Run k-means with k-means++ init and ``n_restarts`` restarts.

    Returns ``(labels, centroids, inertia)`` for the best restart
    (lowest within-cluster sum of squares).
    """
    if rng is None:
        rng = np.random.default_rng(0)
    n_samples, _n_features = data.shape
    if k < 1:
        raise ValueError(f"k must be >= 1, got {k}")
    if n_samples < k:
        raise ValueError(f"Need at least k={k} samples, got {n_samples}")

    best_labels: np.ndarray | None = None
    best_centroids: np.ndarray | None = None
    best_inertia = float("inf")

    for _ in range(n_restarts):
        centroids = _kmeans_pp_init(data, k, rng)
        prev_inertia = float("inf")
        labels = np.zeros(n_samples, dtype=np.int64)

        for _it in range(max_iter):
            d2 = _pairwise_distances_sq(data, centroids)
            labels = np.argmin(d2, axis=1).astype(np.int64)
            new_centroids = np.empty_like(centroids)
            for j in range(k):
                mask = labels == j
                if not np.any(mask):
                    new_centroids[j] = data[rng.integers(0, n_samples)]
                else:
                    new_centroids[j] = data[mask].mean(axis=0)
            inertia = float(np.sum(np.min(_pairwise_distances_sq(data, new_centroids), axis=1)))
            shift = float(np.linalg.norm(new_centroids - centroids))
            centroids = new_centroids
            if shift <= tol or abs(prev_inertia - inertia) <= tol:
                prev_inertia = inertia
                break
            prev_inertia = inertia

        if prev_inertia < best_inertia:
            best_inertia = prev_inertia
            best_labels = labels.copy()
            best_centroids = centroids.copy()

    assert best_labels is not None and best_centroids is not None
    return best_labels, best_centroids, best_inertia


def _kmeans_pp_init(data: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    """k-means++ seeding for stable convergence."""
    n_samples = data.shape[0]
    centroids = np.empty((k, data.shape[1]), dtype=data.dtype)
    first = int(rng.integers(0, n_samples))
    centroids[0] = data[first]
    closest_sq = _pairwise_distances_sq(data, centroids[:1]).flatten()
    for j in range(1, k):
        total = float(closest_sq.sum())
        if total <= 0:
            centroids[j] = data[int(rng.integers(0, n_samples))]
        else:
            probs = closest_sq / total
            idx = int(rng.choice(n_samples, p=probs))
            centroids[j] = data[idx]
        new_dist = _pairwise_distances_sq(data, centroids[j : j + 1]).flatten()
        closest_sq = np.minimum(closest_sq, new_dist)
    return centroids


def silhouette_score(data: np.ndarray, labels: np.ndarray) -> float:
    """Average silhouette score across samples (Rousseeuw 1987).

    Returns ``nan`` when fewer than 2 clusters are present or when
    any cluster contains a single point (silhouette is undefined for
    singletons in that cluster).
    """
    unique_labels = np.unique(labels)
    if unique_labels.size < 2:
        return float("nan")

    n_samples = data.shape[0]
    d = np.sqrt(_pairwise_distances_sq(data, data))

    s_values = np.zeros(n_samples, dtype=float)
    for i in range(n_samples):
        own = labels[i]
        own_mask = labels == own
        own_mask[i] = False
        if not np.any(own_mask):
            s_values[i] = 0.0
            continue
        a = float(d[i, own_mask].mean())
        b_candidates = []
        for lab in unique_labels:
            if lab == own:
                continue
            mask = labels == lab
            if not np.any(mask):
                continue
            b_candidates.append(float(d[i, mask].mean()))
        b = min(b_candidates)
        denom = max(a, b)
        s_values[i] = 0.0 if denom == 0 else (b - a) / denom

    return float(s_values.mean())


def cluster_composition(rows: list[BenchmarkRow], labels: np.ndarray) -> list[dict[str, Any]]:
    """Tabulate adapter-class membership per k-means cluster.

    For each cluster, returns a dict with ``cluster``, ``size``,
    ``composition`` (mapping adapter class -> count), and
    ``dominant_class`` (adapter class with the largest share, or
    ``"mixed"`` if no class exceeds 50%).
    """
    out: list[dict[str, Any]] = []
    for cluster_id in sorted(set(int(x) for x in labels)):
        members = [r for r, lab in zip(rows, labels, strict=False) if int(lab) == cluster_id]
        composition: dict[str, int] = defaultdict(int)
        for r in members:
            composition[r.klass] += 1
        size = len(members)
        if size == 0:
            dominant = "empty"
        else:
            best_class, best_n = max(composition.items(), key=lambda kv: kv[1])
            dominant = best_class if best_n / size > 0.5 else "mixed"
        out.append(
            {
                "cluster": cluster_id,
                "size": size,
                "composition": dict(composition),
                "dominant_class": dominant,
            }
        )
    return out


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 2:
        return float("nan")
    if np.std(x) <= 0 or np.std(y) <= 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def conditional_correlations(matrix: np.ndarray, mask: np.ndarray) -> dict[str, float]:
    """Pearson correlations between every pair of axes within ``mask``."""
    sub = matrix[mask]
    out: dict[str, float] = {}
    for a, b in _PAIRS:
        ix = _AXES.index(a)
        iy = _AXES.index(b)
        out[f"{a}-{b}"] = pearson(sub[:, ix], sub[:, iy])
    return out


def dropout_breakdown(rows: list[BenchmarkRow]) -> dict[str, Any]:
    """Tabulate which rows were dropped (any axis missing) by class/params."""
    by_class: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "dropped": 0})
    by_params: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"total": 0, "dropped": 0}
    )
    for r in rows:
        by_class[r.klass]["total"] += 1
        by_params[(r.klass, r.params)]["total"] += 1
        if not r.is_valid:
            by_class[r.klass]["dropped"] += 1
            by_params[(r.klass, r.params)]["dropped"] += 1

    return {
        "by_class": dict(by_class),
        "by_params": [
            {
                "class": klass,
                "params": params,
                "total": stats["total"],
                "dropped": stats["dropped"],
            }
            for (klass, params), stats in sorted(by_params.items())
        ],
    }


def analyse(rows: list[BenchmarkRow], rng_seed: int = 0) -> dict[str, Any]:
    """Run the full pre-registered analysis on a benchmark dump."""
    rng = np.random.default_rng(rng_seed)

    valid = [r for r in rows if r.is_valid]
    n_total = len(rows)
    n_valid = len(valid)
    if n_valid < 2:
        raise ValueError(f"Need at least 2 valid points for atlas analysis, got {n_valid}")

    matrix = np.array([r.vector for r in valid], dtype=float)
    scaled, axis_mean, axis_std = standardise(matrix)
    pca = pca_via_svd(scaled)

    silhouette_per_k: dict[int, float] = {}
    labels_per_k: dict[int, np.ndarray] = {}
    inertia_per_k: dict[int, float] = {}
    for k in _K_GRID:
        labels, _centroids, inertia = kmeans(pca["whitened"], k, rng=rng)
        silhouette_per_k[k] = silhouette_score(pca["whitened"], labels)
        labels_per_k[k] = labels
        inertia_per_k[k] = inertia

    finite_silhouettes = {k: v for k, v in silhouette_per_k.items() if not np.isnan(v)}
    if finite_silhouettes:
        k_star = max(finite_silhouettes, key=lambda k: finite_silhouettes[k])
    else:
        k_star = _K_GRID[0]

    composition_kstar = cluster_composition(valid, labels_per_k[k_star])

    global_corr = conditional_correlations(matrix, np.ones(matrix.shape[0], dtype=bool))
    cluster_corr: list[dict[str, Any]] = []
    for entry in composition_kstar:
        cid = entry["cluster"]
        mask = labels_per_k[k_star] == cid
        cluster_corr.append(
            {
                "cluster": cid,
                "size": int(mask.sum()),
                "correlations": conditional_correlations(matrix, mask),
            }
        )
    class_corr: list[dict[str, Any]] = []
    classes = sorted({r.klass for r in valid})
    valid_classes = np.array([r.klass for r in valid])
    for klass in classes:
        mask = valid_classes == klass
        class_corr.append(
            {
                "class": klass,
                "size": int(mask.sum()),
                "correlations": conditional_correlations(matrix, mask),
            }
        )

    dropouts = dropout_breakdown(rows)

    return {
        "n_total": n_total,
        "n_valid": n_valid,
        "n_dropped": n_total - n_valid,
        "axes": list(_AXES),
        "axis_mean": axis_mean.tolist(),
        "axis_std": axis_std.tolist(),
        "pca": {
            "explained_variance_ratio": pca["explained_variance_ratio"].tolist(),
            "cumulative_ratio": pca["cumulative_ratio"].tolist(),
            "components": pca["components"].tolist(),
        },
        "kmeans": {
            "k_grid": list(_K_GRID),
            "silhouette": {str(k): silhouette_per_k[k] for k in _K_GRID},
            "inertia": {str(k): inertia_per_k[k] for k in _K_GRID},
            "k_star": int(k_star),
            "composition_at_k_star": composition_kstar,
        },
        "correlations": {
            "global": global_corr,
            "by_cluster_at_k_star": cluster_corr,
            "by_adapter_class": class_corr,
        },
        "dropouts": dropouts,
    }


def _fmt(value: float) -> str:
    if isinstance(value, float) and np.isnan(value):
        return "  n/a"
    return f"{value:+.4f}"


def print_report(result: dict[str, Any]) -> None:
    """Pretty-print the analysis result on stdout."""
    n_total = result["n_total"]
    n_valid = result["n_valid"]
    n_dropped = result["n_dropped"]

    print("Atlas geometry analysis (v0.7.2a0)")
    print("=" * 64)
    print()
    print(f"Sample: {n_valid}/{n_total} fully-valid points (dropped: {n_dropped})")
    print()
    print("--- PCA (z-scored data) ---")
    print(f"  {'comp':<6} {'lambda':>10} {'cumulative':>12}")
    print(f"  {'-' * 6} {'-' * 10} {'-' * 12}")
    ratios = result["pca"]["explained_variance_ratio"]
    cumul = result["pca"]["cumulative_ratio"]
    for i, (r, c) in enumerate(zip(ratios, cumul, strict=False), start=1):
        print(f"  PC{i:<4} {r:>10.4f} {c:>12.4f}")
    if len(cumul) >= 2:
        print(f"\n  lambda_1     = {ratios[0]:.4f}")
        print(f"  lambda_1+_2 = {cumul[1]:.4f}")
    print()
    print("--- K-means + silhouette ---")
    print(f"  {'k':>3} {'silhouette':>11} {'inertia':>11}")
    print(f"  {'-' * 3} {'-' * 11} {'-' * 11}")
    for k in result["kmeans"]["k_grid"]:
        s = result["kmeans"]["silhouette"][str(k)]
        inertia = result["kmeans"]["inertia"][str(k)]
        s_str = "n/a" if np.isnan(s) else f"{s:+.4f}"
        print(f"  {k:>3} {s_str:>11} {inertia:>11.4f}")
    k_star = result["kmeans"]["k_star"]
    s_star = result["kmeans"]["silhouette"][str(k_star)]
    print(f"\n  k* = {k_star}    s(k*) = {s_star:+.4f}")
    print()
    print(f"--- Cluster composition at k* = {k_star} ---")
    for entry in result["kmeans"]["composition_at_k_star"]:
        comp_str = ", ".join(f"{c}={n}" for c, n in sorted(entry["composition"].items()))
        print(
            f"  cluster {entry['cluster']}: n={entry['size']:>3} "
            f"dominant={entry['dominant_class']:<18} [{comp_str}]"
        )
    print()
    print("--- Pairwise Pearson correlations ---")
    print(f"  {'pair':<22} {'global':>10}")
    print(f"  {'-' * 22} {'-' * 10}")
    for pair, value in result["correlations"]["global"].items():
        print(f"  {pair:<22} {_fmt(value):>10}")
    print()
    pair_names = [f"{a}-{b}" for a, b in _PAIRS]
    print("--- Conditional correlations by cluster ---")
    print(f"  {'cluster':>8} {'n':>4} " + " ".join(f"{name:>22}" for name in pair_names))
    for entry in result["correlations"]["by_cluster_at_k_star"]:
        cid = entry["cluster"]
        n = entry["size"]
        vals = [_fmt(entry["correlations"][f"{a}-{b}"]) for a, b in _PAIRS]
        print(f"  {cid:>8} {n:>4} " + " ".join(f"{v:>22}" for v in vals))
    print()
    print("--- Conditional correlations by adapter class ---")
    print(f"  {'class':<18} {'n':>4} " + " ".join(f"{name:>22}" for name in pair_names))
    for entry in result["correlations"]["by_adapter_class"]:
        klass = entry["class"]
        n = entry["size"]
        vals = [_fmt(entry["correlations"][f"{a}-{b}"]) for a, b in _PAIRS]
        print(f"  {klass:<18} {n:>4} " + " ".join(f"{v:>22}" for v in vals))
    print()
    print("--- Dropouts by adapter class ---")
    for klass, stats in sorted(result["dropouts"]["by_class"].items()):
        total = stats["total"]
        dropped = stats["dropped"]
        rate = dropped / total if total else float("nan")
        print(f"  {klass:<18} {dropped:>3}/{total:<3} ({rate:.0%})")
    print()
    print("Thresholds and verdict are NOT applied here.")
    print("See docs/ATLAS_GEOMETRY.md to interpret these numbers.")


_DEFAULT_INPUT = Path(__file__).resolve().parent.parent / "docs" / "benchmarks" / "v0.7.2a0.csv"
_DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent.parent / "docs" / "benchmarks" / "atlas_geometry_v0.7.2a0.json"
)


def write_json(result: dict[str, Any], path: Path) -> None:
    """Persist the analysis result as a UTF-8 JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)

    def _convert(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {str(k): _convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_convert(v) for v in obj]
        if isinstance(obj, tuple):
            return [_convert(v) for v in obj]
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, float) and np.isnan(obj):
            return None
        return obj

    with path.open("w", encoding="utf-8") as fh:
        json.dump(_convert(result), fh, indent=2, ensure_ascii=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Atlas geometry analysis (PCA + k-means) for autonometrics."
    )
    csv_rel = _DEFAULT_INPUT.relative_to(_DEFAULT_INPUT.parents[2])
    out_rel = _DEFAULT_OUTPUT.relative_to(_DEFAULT_OUTPUT.parents[2])
    parser.add_argument(
        "--csv",
        type=Path,
        default=_DEFAULT_INPUT,
        help=f"Input CSV (default: {csv_rel}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=_DEFAULT_OUTPUT,
        help=f"Output JSON (default: {out_rel}).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="RNG seed for k-means restarts (default: 0).",
    )
    args = parser.parse_args(argv)

    if not args.csv.is_file():
        parser.error(f"CSV not found: {args.csv}")

    rows = load_csv(args.csv)
    result = analyse(rows, rng_seed=args.seed)
    print_report(result)
    write_json(result, args.output)
    print(f"\nReport saved to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
