"""Smoke tests for ``examples/constraint_density_plot.py``.

The plot script depends on matplotlib, which is an optional extra
(``autonometrics[viz]``). These tests are skipped automatically when
matplotlib is not installed, so the rest of the suite stays runnable
on a minimal install.
"""

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
    plot_path = repo_root / "examples" / "constraint_density_plot.py"
    spec = importlib.util.spec_from_file_location("constraint_density_plot", plot_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load constraint plot at {plot_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["constraint_density_plot"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def plot() -> ModuleType:
    return _load_plot()


@pytest.fixture
def mini_csv(tmp_path: Path) -> Path:
    csv_path = tmp_path / "constraint_density_mini.csv"
    rows = [
        ["n_nodes", "k", "seed", "constraint", "notes"],
        ["10", "1", "0", "0.100000", ""],
        ["10", "1", "1", "0.150000", ""],
        ["10", "5", "0", "0.900000", ""],
        ["10", "5", "1", "0.950000", ""],
        ["10", "9", "0", "1.000000", ""],
        ["10", "9", "1", "1.000000", ""],
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerows(rows)
    return csv_path


def test_load_csv_coerces_numeric_columns(plot: ModuleType, mini_csv: Path) -> None:
    rows = plot.load_csv(mini_csv)
    assert len(rows) == 6
    assert rows[0]["n_nodes"] == 10
    assert rows[0]["k"] == 1
    assert rows[0]["seed"] == 0
    assert rows[0]["constraint"] == 0.1


def test_aggregate_collapses_seeds_per_k(plot: ModuleType, mini_csv: Path) -> None:
    rows = plot.load_csv(mini_csv)
    aggregated = plot.aggregate(rows)
    assert len(aggregated) == 3
    k_values = [a["k"] for a in aggregated]
    assert k_values == sorted(k_values)
    for a in aggregated:
        assert a["n_valid"] == 2


def test_render_writes_png(plot: ModuleType, mini_csv: Path, tmp_path: Path) -> None:
    rows = plot.load_csv(mini_csv)
    out = tmp_path / "fig.png"
    plot.render(rows, out)
    assert out.is_file()
    assert out.stat().st_size > 1024


def test_render_rejects_empty_csv(plot: ModuleType, tmp_path: Path) -> None:
    empty_csv = tmp_path / "empty.csv"
    with empty_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["n_nodes", "k", "seed", "constraint", "notes"])
        writer.writerow(["10", "1", "0", "", "degenerate"])
    rows = plot.load_csv(empty_csv)
    out = tmp_path / "fig.png"
    with pytest.raises(ValueError):
        plot.render(rows, out)
