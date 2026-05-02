"""Smoke tests for ``examples/saturation_plot.py``.

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
    plot_path = repo_root / "examples" / "saturation_plot.py"
    spec = importlib.util.spec_from_file_location("saturation_plot", plot_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load saturation plot at {plot_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["saturation_plot"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def plot() -> ModuleType:
    return _load_plot()


@pytest.fixture
def mini_csv(tmp_path: Path) -> Path:
    csv_path = tmp_path / "saturation_mini.csv"
    rows = [
        ["rule", "p_noise", "seed", "closure", "memory", "notes"],
        ["110", "0.0000", "0", "1.000000", "0.600000", ""],
        ["110", "0.0000", "1", "1.000000", "0.595000", ""],
        ["110", "0.1000", "0", "0.700000", "0.580000", ""],
        ["110", "0.1000", "1", "0.690000", "0.575000", ""],
        ["110", "0.3000", "0", "0.300000", "0.520000", ""],
        ["110", "0.3000", "1", "0.290000", "0.515000", ""],
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerows(rows)
    return csv_path


def test_load_csv_coerces_numeric_columns(plot: ModuleType, mini_csv: Path) -> None:
    rows = plot.load_csv(mini_csv)
    assert len(rows) == 6
    assert rows[0]["rule"] == 110
    assert rows[0]["seed"] == 0
    assert rows[0]["p_noise"] == 0.0
    assert rows[0]["closure"] == 1.0


def test_aggregate_collapses_seeds_per_p(plot: ModuleType, mini_csv: Path) -> None:
    rows = plot.load_csv(mini_csv)
    aggregated = plot.aggregate(rows)
    assert len(aggregated) == 3
    p_values = [a["p_noise"] for a in aggregated]
    assert p_values == sorted(p_values)
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
        writer.writerow(["rule", "p_noise", "seed", "closure", "memory", "notes"])
        writer.writerow(["110", "0.0", "0", "", "", "degenerate"])
    rows = plot.load_csv(empty_csv)
    out = tmp_path / "fig.png"
    with pytest.raises(ValueError):
        plot.render(rows, out)
