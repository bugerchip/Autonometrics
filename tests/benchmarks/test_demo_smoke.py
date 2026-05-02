"""Smoke tests for ``examples/benchmark_demo.py``.

The demo lives outside the installable package (``examples/`` is not
copied into the wheel), so the test loads it as a module via
``importlib`` from its source path. We run only the ``--quick`` subset
to keep CI fast; a full benchmark run is exercised manually before
each release.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest


def _load_demo() -> ModuleType:
    """Load ``examples/benchmark_demo.py`` as a module by file path."""
    repo_root = Path(__file__).resolve().parents[2]
    demo_path = repo_root / "examples" / "benchmark_demo.py"
    spec = importlib.util.spec_from_file_location("benchmark_demo", demo_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load benchmark demo at {demo_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["benchmark_demo"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def demo() -> ModuleType:
    return _load_demo()


def test_quick_run_yields_three_points(demo: ModuleType) -> None:
    points = demo.run_benchmark(quick=True)
    assert len(points) == 3
    classes = {p.system_class for p in points}
    assert classes == {"ECASystem", "KauffmanNetwork", "PeriodicCycle"}


def test_quick_run_points_have_valid_fields(demo: ModuleType) -> None:
    points = demo.run_benchmark(quick=True)
    for p in points:
        assert p.seed == 0
        if p.closure is not None:
            assert 0.0 <= p.closure <= 1.0
        if p.memory is not None:
            assert 0.0 <= p.memory <= 1.0
        if p.constraint is not None:
            assert 0.0 <= p.constraint <= 1.0
        if p.persistence is not None:
            assert 0.0 <= p.persistence <= 1.0
        assert p.quadrant in {"drift", "clockwork", "turbulence", "autopoietic", "n/a"}


def test_write_csv_produces_well_formed_file(demo: ModuleType, tmp_path: Path) -> None:
    points = demo.run_benchmark(quick=True)
    out = tmp_path / "out.csv"
    demo.write_csv(points, out)
    assert out.is_file()
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1 + len(points)
    header = lines[0].split(",")
    assert header == [
        "class",
        "params",
        "seed",
        "closure",
        "memory",
        "constraint",
        "persistence",
        "quadrant",
        "notes",
    ]


def test_summarise_returns_expected_keys(demo: ModuleType) -> None:
    points = demo.run_benchmark(quick=True)
    summary = demo.summarise(points)
    assert summary["n_total"] == 3
    assert summary["n_valid"] <= summary["n_total"]
    assert "correlations" in summary
    pairs = summary["correlations"]
    assert set(pairs.keys()) == {
        "closure-memory",
        "closure-constraint",
        "closure-persistence",
        "memory-constraint",
        "memory-persistence",
        "constraint-persistence",
    }
    for stats in pairs.values():
        assert {"n", "pearson", "spearman", "flag"} <= stats.keys()
        assert stats["flag"] in {"OK", "WARN", "FAIL", "N/A"}
    assert summary["flag"] in {"OK", "WARN", "FAIL", "N/A"}
    assert isinstance(summary["quadrants"], dict)


def test_quadrant_of_handles_missing_values(demo: ModuleType) -> None:
    assert demo.quadrant_of(None, 0.5) == "n/a"
    assert demo.quadrant_of(0.5, None) == "n/a"
    assert demo.quadrant_of(0.8, 0.8) == "autopoietic"
    assert demo.quadrant_of(0.8, 0.2) == "clockwork"
    assert demo.quadrant_of(0.2, 0.8) == "turbulence"
    assert demo.quadrant_of(0.2, 0.2) == "drift"


def test_diagnosis_flag_thresholds(demo: ModuleType) -> None:
    assert demo.diagnosis_flag(0.0) == "OK"
    assert demo.diagnosis_flag(0.69) == "OK"
    assert demo.diagnosis_flag(0.7) == "WARN"
    assert demo.diagnosis_flag(0.89) == "WARN"
    assert demo.diagnosis_flag(0.9) == "FAIL"
    assert demo.diagnosis_flag(1.0) == "FAIL"
    assert demo.diagnosis_flag(float("nan")) == "N/A"
