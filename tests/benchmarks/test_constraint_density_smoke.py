"""Smoke tests for ``examples/constraint_density_diagnostic.py``.

The diagnostic lives outside the installable package, so the test
loads it as a module via ``importlib`` from its source path. We run
only the ``--quick`` density sweep to keep CI fast; the full sweep
is exercised manually before each release that ships a snapshot
under ``docs/benchmarks/``.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest


def _load_diagnostic() -> ModuleType:
    """Load ``examples/constraint_density_diagnostic.py`` as a module by file path."""
    repo_root = Path(__file__).resolve().parents[2]
    src = repo_root / "examples" / "constraint_density_diagnostic.py"
    spec = importlib.util.spec_from_file_location("constraint_density_diagnostic", src)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load constraint diagnostic at {src}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["constraint_density_diagnostic"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def diag() -> ModuleType:
    return _load_diagnostic()


def test_default_k_values_span_one_to_n_minus_one(diag: ModuleType) -> None:
    """Default sweep covers the full open density interval (K = 1 .. n - 1)."""
    assert diag._default_k_values(10) == (1, 2, 3, 4, 5, 6, 7, 8, 9)
    assert diag._default_k_values(4) == (1, 2, 3)


def test_quick_k_values_three_points(diag: ModuleType) -> None:
    """Quick mode produces a low/middle/high triple covering the full range."""
    quick = diag._quick_k_values(10)
    assert len(quick) == 3
    assert quick[0] == 1
    assert quick[-1] == 9
    assert min(quick) == 1
    assert max(quick) == 9


def test_quick_sweep_returns_expected_count(diag: ModuleType) -> None:
    """``--quick`` mode emits ``len(K) * n_seeds`` measurements."""
    k_values = diag._quick_k_values(diag._DEFAULT_N_NODES)
    points = diag.run_sweep(
        n_nodes=diag._DEFAULT_N_NODES,
        k_values=k_values,
        n_seeds=diag._QUICK_N_SEEDS,
        n_steps=diag._DEFAULT_N_STEPS,
    )
    assert len(points) == len(k_values) * diag._QUICK_N_SEEDS
    for p in points:
        assert p.n_nodes == diag._DEFAULT_N_NODES
        assert p.k in k_values
        if p.constraint is not None:
            assert 0.0 <= p.constraint <= 1.0


def test_low_k_walks_lower_boundary(diag: ModuleType) -> None:
    """Sparse Kauffman networks (K=1) sit close to the trivial-zero theorem."""
    points = diag.run_sweep(
        n_nodes=10,
        k_values=(1,),
        n_seeds=10,
        n_steps=diag._DEFAULT_N_STEPS,
    )
    scores = [p.constraint for p in points if p.constraint is not None]
    assert scores, "expected at least one valid constraint measurement at K=1"
    mean_low = float(np.mean(scores))
    assert mean_low < 0.4, f"expected K=1 mean to walk lower boundary, got {mean_low:.3f}"


def test_high_k_saturates_upper_boundary(diag: ModuleType) -> None:
    """Dense Kauffman networks (K=n-1) saturate the symmetric-neighbour theorem."""
    points = diag.run_sweep(
        n_nodes=10,
        k_values=(9,),
        n_seeds=5,
        n_steps=diag._DEFAULT_N_STEPS,
    )
    scores = [p.constraint for p in points if p.constraint is not None]
    assert scores, "expected at least one valid constraint measurement at K=9"
    for score in scores:
        assert score >= 0.99, f"expected K=9 to saturate the upper boundary, got {score:.4f}"


def test_curve_walks_from_low_to_high(diag: ModuleType) -> None:
    """The mean constraint must rise meaningfully from K=1 to K=n-1."""
    points = diag.run_sweep(
        n_nodes=10,
        k_values=(1, 9),
        n_seeds=5,
        n_steps=diag._DEFAULT_N_STEPS,
    )
    by_k: dict[int, list[float]] = {}
    for p in points:
        if p.constraint is not None:
            by_k.setdefault(p.k, []).append(p.constraint)
    assert 1 in by_k and 9 in by_k
    rise = float(np.mean(by_k[9])) - float(np.mean(by_k[1]))
    assert rise > 0.5, f"expected substantial rise across density, got {rise:.3f}"


def test_write_csv_produces_well_formed_file(diag: ModuleType, tmp_path: Path) -> None:
    """CSV writer emits the expected header and one row per measurement."""
    k_values = diag._quick_k_values(diag._DEFAULT_N_NODES)
    points = diag.run_sweep(
        n_nodes=diag._DEFAULT_N_NODES,
        k_values=k_values,
        n_seeds=diag._QUICK_N_SEEDS,
        n_steps=diag._DEFAULT_N_STEPS,
    )
    out = tmp_path / "constraint_density.csv"
    diag.write_csv(points, out)
    assert out.is_file()
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1 + len(points)
    header = lines[0].split(",")
    assert header == ["n_nodes", "k", "seed", "constraint", "notes"]


def test_aggregate_groups_by_k(diag: ModuleType) -> None:
    """Aggregate must produce one bucket per swept K value."""
    k_values = diag._quick_k_values(diag._DEFAULT_N_NODES)
    points = diag.run_sweep(
        n_nodes=diag._DEFAULT_N_NODES,
        k_values=k_values,
        n_seeds=diag._QUICK_N_SEEDS,
        n_steps=diag._DEFAULT_N_STEPS,
    )
    stats = diag.aggregate(points)
    assert set(stats.keys()) == set(k_values)
    for row in stats.values():
        assert "constraint_mean" in row
        assert "constraint_std" in row
        assert row["n_total"] == diag._QUICK_N_SEEDS


def test_diagnosis_line_flags_ok_on_full_sweep(diag: ModuleType) -> None:
    """A sweep that walks 0 -> 1 monotonically must trigger the [OK] verdict."""
    k_values = diag._default_k_values(diag._DEFAULT_N_NODES)
    points = diag.run_sweep(
        n_nodes=diag._DEFAULT_N_NODES,
        k_values=k_values,
        n_seeds=5,
        n_steps=diag._DEFAULT_N_STEPS,
    )
    stats = diag.aggregate(points)
    line = diag.diagnosis_line(stats)
    assert line.startswith("[OK]"), f"expected [OK] verdict, got: {line}"
