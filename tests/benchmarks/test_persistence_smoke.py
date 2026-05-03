"""Smoke tests for ``examples/persistence_diagnostic.py``."""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest


def _load_diagnostic() -> ModuleType:
    repo_root = Path(__file__).resolve().parents[2]
    diag_path = repo_root / "examples" / "persistence_diagnostic.py"
    spec = importlib.util.spec_from_file_location("persistence_diagnostic", diag_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load diagnostic at {diag_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["persistence_diagnostic"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def diag() -> ModuleType:
    return _load_diagnostic()


def test_quick_run_yields_three_couplings(diag: ModuleType) -> None:
    points = diag.run_sweep(
        couplings=diag._QUICK_COUPLINGS,
        n_seeds=diag._QUICK_N_SEEDS,
        n_nodes=diag._DEFAULT_N_NODES,
        k=diag._DEFAULT_K,
        n_steps=diag._DEFAULT_N_STEPS,
    )
    assert len(points) == len(diag._QUICK_COUPLINGS) * diag._QUICK_N_SEEDS
    couplings = {p.coupling for p in points}
    assert couplings == set(diag._QUICK_COUPLINGS)


def test_full_coupling_one_saturates_to_one(diag: ModuleType) -> None:
    """At coupling = 1 the focal flip is invisible; persistence -> 1.0."""
    points = diag.run_sweep(
        couplings=(1.0,),
        n_seeds=5,
        n_nodes=diag._DEFAULT_N_NODES,
        k=diag._DEFAULT_K,
        n_steps=diag._DEFAULT_N_STEPS,
    )
    valid = [p.persistence for p in points if p.persistence is not None]
    assert valid, "expected at least one valid measurement at coupling=1"
    assert max(valid) >= 0.9


def test_write_csv_produces_well_formed_file(
    diag: ModuleType, tmp_path: Path
) -> None:
    points = diag.run_sweep(
        couplings=diag._QUICK_COUPLINGS,
        n_seeds=diag._QUICK_N_SEEDS,
        n_nodes=diag._DEFAULT_N_NODES,
        k=diag._DEFAULT_K,
        n_steps=diag._DEFAULT_N_STEPS,
    )
    out = tmp_path / "out.csv"
    diag.write_csv(points, out)
    assert out.is_file()
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1 + len(points)
    header = lines[0].split(",")
    assert header == ["coupling", "seed", "persistence", "notes"]


def test_aggregate_handles_full_sweep(diag: ModuleType) -> None:
    points = diag.run_sweep(
        couplings=diag._QUICK_COUPLINGS,
        n_seeds=diag._QUICK_N_SEEDS,
        n_nodes=diag._DEFAULT_N_NODES,
        k=diag._DEFAULT_K,
        n_steps=diag._DEFAULT_N_STEPS,
    )
    stats = diag.aggregate(points)
    assert set(stats.keys()) == set(diag._QUICK_COUPLINGS)
    for entry in stats.values():
        assert "n_total" in entry
        assert "n_valid" in entry
        assert "mean" in entry
        assert "std" in entry


def test_diagnosis_line_returns_a_string(diag: ModuleType) -> None:
    points = diag.run_sweep(
        couplings=diag._QUICK_COUPLINGS,
        n_seeds=diag._QUICK_N_SEEDS,
        n_nodes=diag._DEFAULT_N_NODES,
        k=diag._DEFAULT_K,
        n_steps=diag._DEFAULT_N_STEPS,
    )
    line = diag.diagnosis_line(diag.aggregate(points))
    assert isinstance(line, str)
    assert any(tag in line for tag in ("[OK]", "[PARTIAL]", "[UNEXPECTED]", "[N/A]"))
