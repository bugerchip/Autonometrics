"""Smoke tests for ``examples/atlas_geometry_plot.py``."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest


def _load_plot() -> ModuleType:
    repo_root = Path(__file__).resolve().parents[2]
    src_path = repo_root / "examples" / "atlas_geometry_plot.py"
    spec = importlib.util.spec_from_file_location("atlas_geometry_plot", src_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load atlas_geometry_plot at {src_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["atlas_geometry_plot"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def plot() -> ModuleType:
    return _load_plot()


def test_load_report_returns_dict(plot: ModuleType) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    json_path = repo_root / "docs" / "benchmarks" / "atlas_geometry_v0.7.2a0.json"
    if not json_path.is_file():
        pytest.skip("v0.7.2a0 atlas JSON not available")
    report = plot.load_report(json_path)
    assert isinstance(report, dict)
    assert "pca" in report
    assert "kmeans" in report


def test_render_produces_png(plot: ModuleType, tmp_path: Path) -> None:
    pytest.importorskip("matplotlib")
    repo_root = Path(__file__).resolve().parents[2]
    json_path = repo_root / "docs" / "benchmarks" / "atlas_geometry_v0.7.2a0.json"
    csv_path = repo_root / "docs" / "benchmarks" / "v0.7.2a0.csv"
    if not json_path.is_file() or not csv_path.is_file():
        pytest.skip("v0.7.2a0 snapshots not available")

    report = plot.load_report(json_path)
    projection = plot._project_for_biplot(csv_path, report, rng_seed=0)

    out = tmp_path / "atlas.png"
    plot.render(report, projection, out)
    assert out.is_file()
    assert out.stat().st_size > 1000
