"""Smoke tests for ``examples/atlas_geometry.py``.

The script is loaded from its source path because ``examples/`` is
not part of the installed wheel. We exercise:

- the PCA reconstruction quality on synthetic data,
- the k-means convergence on a simple separated cloud,
- the silhouette ranking,
- the round-trip from CSV -> ``analyse`` -> ``write_json``.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest


def _load_atlas() -> ModuleType:
    repo_root = Path(__file__).resolve().parents[2]
    src_path = repo_root / "examples" / "atlas_geometry.py"
    spec = importlib.util.spec_from_file_location("atlas_geometry", src_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load atlas_geometry at {src_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["atlas_geometry"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def atlas() -> ModuleType:
    return _load_atlas()


def test_pca_recovers_known_directions(atlas: ModuleType) -> None:
    """A 2D anisotropic Gaussian should yield lambda_1 close to its known share."""
    rng = np.random.default_rng(0)
    n = 500
    a = rng.normal(0.0, 3.0, size=n)
    b = rng.normal(0.0, 1.0, size=n)
    matrix = np.stack([a, b, 0.5 * a + 0.1 * b, 0.1 * a - 0.05 * b], axis=1)
    scaled, _mean, _std = atlas.standardise(matrix)
    pca = atlas.pca_via_svd(scaled)
    ratios = pca["explained_variance_ratio"]
    assert ratios[0] > 0.55
    assert ratios.sum() == pytest.approx(1.0, abs=1e-9)


def test_kmeans_separates_two_gaussian_blobs(atlas: ModuleType) -> None:
    rng = np.random.default_rng(1)
    a = rng.normal(loc=-3.0, scale=0.3, size=(60, 4))
    b = rng.normal(loc=+3.0, scale=0.3, size=(60, 4))
    data = np.vstack([a, b])
    labels, centroids, inertia = atlas.kmeans(data, k=2, n_restarts=5, rng=np.random.default_rng(0))
    cluster_a = set(labels[:60].tolist())
    cluster_b = set(labels[60:].tolist())
    assert len(cluster_a) == 1
    assert len(cluster_b) == 1
    assert cluster_a != cluster_b
    assert centroids.shape == (2, 4)
    assert inertia > 0


def test_silhouette_high_for_separated_blobs(atlas: ModuleType) -> None:
    rng = np.random.default_rng(2)
    a = rng.normal(loc=-5.0, scale=0.2, size=(40, 3))
    b = rng.normal(loc=+5.0, scale=0.2, size=(40, 3))
    data = np.vstack([a, b])
    labels = np.array([0] * 40 + [1] * 40)
    score = atlas.silhouette_score(data, labels)
    assert score > 0.8


def test_silhouette_low_for_random_labels(atlas: ModuleType) -> None:
    rng = np.random.default_rng(3)
    data = rng.normal(size=(60, 4))
    labels = rng.integers(0, 3, size=60)
    score = atlas.silhouette_score(data, labels)
    assert -0.5 < score < 0.3


def test_load_csv_handles_v0_7_2a0_snapshot(atlas: ModuleType) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    csv_path = repo_root / "docs" / "benchmarks" / "v0.7.2a0.csv"
    if not csv_path.is_file():
        pytest.skip("v0.7.2a0 snapshot not available")
    rows = atlas.load_csv(csv_path)
    assert len(rows) > 0
    assert any(r.is_valid for r in rows)


def test_analyse_round_trip(atlas: ModuleType, tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    csv_path = repo_root / "docs" / "benchmarks" / "v0.7.2a0.csv"
    if not csv_path.is_file():
        pytest.skip("v0.7.2a0 snapshot not available")
    rows = atlas.load_csv(csv_path)
    result = atlas.analyse(rows, rng_seed=0)

    assert result["axes"] == ["closure", "memory", "constraint", "persistence"]
    assert 0 < result["n_valid"] <= result["n_total"]
    pca = result["pca"]
    ratios = pca["explained_variance_ratio"]
    assert len(ratios) == 4
    assert sum(ratios) == pytest.approx(1.0, abs=1e-9)

    silhouettes = result["kmeans"]["silhouette"]
    assert set(silhouettes.keys()) == {"2", "3", "4", "5"}

    out = tmp_path / "atlas.json"
    atlas.write_json(result, out)
    assert out.is_file()
    parsed = json.loads(out.read_text(encoding="utf-8"))
    assert parsed["axes"] == result["axes"]
    assert parsed["n_valid"] == result["n_valid"]


def test_dropout_breakdown_totals_match_input(atlas: ModuleType) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    csv_path = repo_root / "docs" / "benchmarks" / "v0.7.2a0.csv"
    if not csv_path.is_file():
        pytest.skip("v0.7.2a0 snapshot not available")
    rows = atlas.load_csv(csv_path)
    info = atlas.dropout_breakdown(rows)
    total_classes = sum(s["total"] for s in info["by_class"].values())
    dropped_classes = sum(s["dropped"] for s in info["by_class"].values())
    assert total_classes == len(rows)
    assert dropped_classes == sum(1 for r in rows if not r.is_valid)
