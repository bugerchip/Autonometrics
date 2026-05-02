"""Smoke tests for ``examples/saturation_diagnostic.py``.

The diagnostic lives outside the installable package, so the test
loads it as a module via ``importlib`` from its source path. We run
only the ``--quick`` noise sweep (3 levels x 2 seeds) to keep CI
fast; the full sweep is exercised manually before each release that
ships a snapshot under ``docs/benchmarks/``.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest


def _load_diagnostic() -> ModuleType:
    """Load ``examples/saturation_diagnostic.py`` as a module by file path."""
    repo_root = Path(__file__).resolve().parents[2]
    src = repo_root / "examples" / "saturation_diagnostic.py"
    spec = importlib.util.spec_from_file_location("saturation_diagnostic", src)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load saturation diagnostic at {src}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["saturation_diagnostic"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def diag() -> ModuleType:
    return _load_diagnostic()


def test_noisy_eca_zero_noise_matches_base(diag: ModuleType) -> None:
    """At p=0 the noisy wrapper must reproduce the underlying ECA exactly."""
    base = diag.ECASystem(rule=110, n_steps=200, width=51, seed=0)
    wrapped = diag.NoisyECA(rule=110, n_steps=200, p_noise=0.0, width=51, seed=0)
    np.testing.assert_array_equal(base.get_state_history(), wrapped.get_state_history())
    np.testing.assert_array_equal(base.get_env_history(), wrapped.get_env_history())


def test_noisy_eca_nonzero_noise_diverges(diag: ModuleType) -> None:
    """At p>0 the noisy state diverges from the base, but env stays intact."""
    base = diag.ECASystem(rule=110, n_steps=500, width=51, seed=0)
    wrapped = diag.NoisyECA(rule=110, n_steps=500, p_noise=0.2, width=51, seed=0)
    base_states = base.get_state_history()
    noisy_states = wrapped.get_state_history()
    diff_fraction = float(np.mean(base_states != noisy_states))
    assert 0.10 < diff_fraction < 0.30, (
        f"expected ~20% bit flips, got {diff_fraction:.3f}"
    )
    np.testing.assert_array_equal(base.get_env_history(), wrapped.get_env_history())


def test_noisy_eca_rejects_invalid_p(diag: ModuleType) -> None:
    """``p_noise`` outside [0, 1] must raise ``ValueError``."""
    with pytest.raises(ValueError):
        diag.NoisyECA(rule=110, n_steps=100, p_noise=-0.1, width=51, seed=0)
    with pytest.raises(ValueError):
        diag.NoisyECA(rule=110, n_steps=100, p_noise=1.1, width=51, seed=0)


def test_quick_sweep_returns_six_points(diag: ModuleType) -> None:
    """``--quick`` mode emits 3 noise levels x 2 seeds = 6 measurements."""
    points = diag.run_sweep(
        rule=110,
        noise_levels=diag._QUICK_NOISE_LEVELS,
        n_seeds=diag._QUICK_N_SEEDS,
        n_steps=500,
    )
    assert len(points) == len(diag._QUICK_NOISE_LEVELS) * diag._QUICK_N_SEEDS
    for p in points:
        assert p.rule == 110
        assert 0.0 <= p.p_noise <= 1.0
        if p.closure is not None:
            assert 0.0 <= p.closure <= 1.0
        if p.memory is not None:
            assert 0.0 <= p.memory <= 1.0


def test_zero_noise_recovers_saturation(diag: ModuleType) -> None:
    """At p=0 the diagnostic should reproduce the saturation wall."""
    points = diag.run_sweep(
        rule=110,
        noise_levels=(0.0,),
        n_seeds=2,
        n_steps=1000,
    )
    closures = [p.closure for p in points if p.closure is not None]
    assert closures, "expected at least one valid closure measurement at p=0"
    for c in closures:
        assert c >= 0.99, f"expected closure ~1.0 at p=0, got {c:.4f}"


def test_high_noise_lowers_closure(diag: ModuleType) -> None:
    """At p=0.4 the closure score must fall noticeably below 1.0."""
    points = diag.run_sweep(
        rule=110,
        noise_levels=(0.0, 0.4),
        n_seeds=2,
        n_steps=1500,
    )
    by_p: dict[float, list[float]] = {}
    for p in points:
        if p.closure is not None:
            by_p.setdefault(p.p_noise, []).append(p.closure)
    assert 0.0 in by_p and 0.4 in by_p
    mean_zero = float(np.mean(by_p[0.0]))
    mean_high = float(np.mean(by_p[0.4]))
    assert mean_zero - mean_high > 0.3, (
        f"expected substantial drop, got {mean_zero:.3f} -> {mean_high:.3f}"
    )


def test_write_csv_produces_well_formed_file(diag: ModuleType, tmp_path: Path) -> None:
    points = diag.run_sweep(
        rule=110,
        noise_levels=diag._QUICK_NOISE_LEVELS,
        n_seeds=diag._QUICK_N_SEEDS,
        n_steps=500,
    )
    out = tmp_path / "saturation.csv"
    diag.write_csv(points, out)
    assert out.is_file()
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1 + len(points)
    header = lines[0].split(",")
    assert header == ["rule", "p_noise", "seed", "closure", "memory", "notes"]


def test_aggregate_groups_by_noise_level(diag: ModuleType) -> None:
    points = diag.run_sweep(
        rule=110,
        noise_levels=diag._QUICK_NOISE_LEVELS,
        n_seeds=diag._QUICK_N_SEEDS,
        n_steps=500,
    )
    stats = diag.aggregate(points)
    assert set(stats.keys()) == set(diag._QUICK_NOISE_LEVELS)
    for row in stats.values():
        assert "closure_mean" in row
        assert "closure_std" in row
        assert "memory_mean" in row
        assert "memory_std" in row
        assert row["n_total"] == diag._QUICK_N_SEEDS
