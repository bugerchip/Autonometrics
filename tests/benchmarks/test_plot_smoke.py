"""Smoke tests for ``examples/benchmark_plot.py``.

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
    plot_path = repo_root / "examples" / "benchmark_plot.py"
    spec = importlib.util.spec_from_file_location("benchmark_plot", plot_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load benchmark plot at {plot_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["benchmark_plot"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def plot() -> ModuleType:
    return _load_plot()


@pytest.fixture
def mini_csv(tmp_path: Path) -> Path:
    csv_path = tmp_path / "mini.csv"
    rows = [
        [
            "class",
            "params",
            "seed",
            "closure",
            "memory",
            "constraint",
            "quadrant",
            "notes",
        ],
        ["ECASystem", "rule=110", "0", "0.950000", "0.600000", "1.000000", "autopoietic", ""],
        ["ECASystem", "rule=30", "0", "1.000000", "0.150000", "1.000000", "clockwork", ""],
        ["KauffmanNetwork", "coupling=0.5", "0", "0.300000", "0.500000", "0.400000", "drift", ""],
        [
            "SimpleAutomaton",
            "self_generated",
            "0",
            "0.980000",
            "0.970000",
            "0.000000",
            "autopoietic",
            "",
        ],
        ["SimpleAutomaton", "external", "0", "0.020000", "0.400000", "0.000000", "drift", ""],
        ["KauffmanNetwork", "coupling=0.0", "0", "", "", "", "n/a", "degenerate"],
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerows(rows)
    return csv_path


@pytest.fixture
def legacy_csv(tmp_path: Path) -> Path:
    """Older CSV (no ``constraint`` column) to confirm backwards compat."""
    csv_path = tmp_path / "legacy.csv"
    rows = [
        ["class", "params", "seed", "closure", "memory", "quadrant", "notes"],
        ["ECASystem", "rule=110", "0", "0.950000", "0.600000", "autopoietic", ""],
        ["KauffmanNetwork", "coupling=0.5", "0", "0.300000", "0.500000", "drift", ""],
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerows(rows)
    return csv_path


def test_load_csv_coerces_floats_and_handles_empty(plot: ModuleType, mini_csv: Path) -> None:
    rows = plot.load_csv(mini_csv)
    assert len(rows) == 6
    assert rows[0]["closure"] == 0.95
    assert rows[0]["constraint"] == 1.0
    assert rows[0]["seed"] == 0
    assert rows[-1]["closure"] is None
    assert rows[-1]["memory"] is None
    assert rows[-1]["constraint"] is None


def test_load_csv_handles_legacy_without_constraint(plot: ModuleType, legacy_csv: Path) -> None:
    rows = plot.load_csv(legacy_csv)
    assert len(rows) == 2
    assert all(r["constraint"] is None for r in rows)


def test_render_writes_png(plot: ModuleType, mini_csv: Path, tmp_path: Path) -> None:
    rows = plot.load_csv(mini_csv)
    out = tmp_path / "fig.png"
    plot.render(rows, out)
    assert out.is_file()
    assert out.stat().st_size > 1024


def test_classify_distinguishes_simple_automaton_modes(plot: ModuleType) -> None:
    assert plot._classify({"class": "SimpleAutomaton", "params": "self_generated"}) == (
        "SimpleAutomaton",
        "self_generated",
    )
    assert plot._classify({"class": "SimpleAutomaton", "params": "external"}) == (
        "SimpleAutomaton",
        "external",
    )
    assert plot._classify({"class": "ECASystem", "params": "rule=110"}) == (
        "ECASystem",
        None,
    )


def test_marker_for_external_is_cross(plot: ModuleType) -> None:
    assert plot._marker_for("external") == "x"
    assert plot._marker_for("self_generated") == "o"
    assert plot._marker_for(None) == "o"


def test_summary_line_includes_pearson_and_flag(plot: ModuleType, mini_csv: Path) -> None:
    rows = plot.load_csv(mini_csv)
    line = plot._summary_line(rows)
    assert "n=" in line
    assert "Pearson" in line
    assert any(flag in line for flag in ("OK", "WARN", "FAIL", "N/A"))
