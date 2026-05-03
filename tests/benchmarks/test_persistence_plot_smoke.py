"""Smoke tests for ``examples/persistence_plot.py``."""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

pytest.importorskip("matplotlib")

import matplotlib  # noqa: E402

matplotlib.use("Agg")


def _load_plot() -> ModuleType:
    repo_root = Path(__file__).resolve().parents[2]
    plot_path = repo_root / "examples" / "persistence_plot.py"
    spec = importlib.util.spec_from_file_location("persistence_plot", plot_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load plot at {plot_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["persistence_plot"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def plot() -> ModuleType:
    return _load_plot()


@pytest.fixture
def mini_csv(tmp_path: Path) -> Path:
    csv_path = tmp_path / "mini.csv"
    rows = [
        ["coupling", "seed", "persistence", "notes"],
        ["0.0000", "0", "1.000000", ""],
        ["0.0000", "1", "1.000000", ""],
        ["0.5000", "0", "0.500000", ""],
        ["0.5000", "1", "0.400000", ""],
        ["1.0000", "0", "1.000000", ""],
        ["1.0000", "1", "1.000000", ""],
        ["0.0000", "2", "", "constant trajectory"],
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerows(rows)
    return csv_path


def test_load_csv_coerces_numeric_columns(plot: ModuleType, mini_csv: Path) -> None:
    rows = plot.load_csv(mini_csv)
    assert len(rows) == 7
    assert rows[0]["coupling"] == 0.0
    assert rows[0]["seed"] == 0
    assert rows[0]["persistence"] == 1.0
    assert rows[-1]["persistence"] is None


def test_aggregate_groups_by_coupling(plot: ModuleType, mini_csv: Path) -> None:
    rows = plot.load_csv(mini_csv)
    aggregated = plot.aggregate(rows)
    assert {a["coupling"] for a in aggregated} == {0.0, 0.5, 1.0}
    for entry in aggregated:
        assert "n_valid" in entry
        assert "persistence_mean" in entry
        assert "persistence_std" in entry


def test_render_writes_png(plot: ModuleType, mini_csv: Path, tmp_path: Path) -> None:
    rows = plot.load_csv(mini_csv)
    out = tmp_path / "fig.png"
    plot.render(rows, out)
    assert out.is_file()
    assert out.stat().st_size > 1024
