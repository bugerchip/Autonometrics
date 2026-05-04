"""Smoke tests for ``examples/cba_env_decouple_experiment.py``.

Loads the script as a module by source path (it lives outside the
installable package) and exercises a tiny grid of measurements
plus the JSON / PNG output paths.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest


def _load_experiment() -> ModuleType:
    repo_root = Path(__file__).resolve().parents[2]
    src_path = repo_root / "examples" / "cba_env_decouple_experiment.py"
    spec = importlib.util.spec_from_file_location(
        "cba_env_decouple_experiment", src_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load experiment script at {src_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["cba_env_decouple_experiment"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def experiment() -> ModuleType:
    return _load_experiment()


def test_measure_cell_returns_two_axes(experiment: ModuleType) -> None:
    cell = experiment.measure_cell(
        period=4, alphabet=4, length=400,
        p_noise=0.5, p_env=0.0, seed=0,
    )
    assert cell.closure is not None
    assert cell.coherence is not None
    assert 0.0 <= cell.closure <= 1.0
    assert 0.0 <= cell.coherence <= 1.0


def test_run_sweep_size(experiment: ModuleType) -> None:
    cells = experiment.run_sweep(
        period=4, alphabet=4, length=400,
        p_noise_values=(0.2, 0.6),
        p_env_values=(0.0, 0.5),
        n_seeds=2,
    )
    assert len(cells) == 8
    assert {c.p_env for c in cells} == {0.0, 0.5}
    assert {c.p_noise for c in cells} == {0.2, 0.6}


def test_analyse_emits_expected_keys(experiment: ModuleType) -> None:
    cells = experiment.run_sweep(
        period=4, alphabet=4, length=400,
        p_noise_values=(0.2, 0.6),
        p_env_values=(0.0, 0.5),
        n_seeds=2,
    )
    result = experiment.analyse(cells)
    expected = {
        "n_total",
        "global_pearson",
        "closure_vs_p_noise_pearson",
        "closure_vs_p_env_pearson",
        "coherence_vs_p_noise_pearson",
        "coherence_vs_p_env_pearson",
        "fixed_p_env_correlations",
        "fixed_p_noise_correlations",
        "cell_correlations",
    }
    assert expected.issubset(result.keys())
    assert result["n_total"] == 8


def test_write_json_round_trip(experiment: ModuleType, tmp_path: Path) -> None:
    cells = experiment.run_sweep(
        period=4, alphabet=4, length=400,
        p_noise_values=(0.5,),
        p_env_values=(0.0, 0.5, 1.0),
        n_seeds=2,
    )
    result = experiment.analyse(cells)
    out = tmp_path / "exp.json"
    experiment.write_json(result, cells, out)
    parsed = json.loads(out.read_text(encoding="utf-8"))
    assert "summary" in parsed
    assert "raw_cells" in parsed
    assert len(parsed["raw_cells"]) == 6


def test_write_scatter_runs_or_skips_cleanly(
    experiment: ModuleType, tmp_path: Path
) -> None:
    cells = experiment.run_sweep(
        period=4, alphabet=4, length=400,
        p_noise_values=(0.3, 0.7),
        p_env_values=(0.0, 0.5, 1.0),
        n_seeds=2,
    )
    out = tmp_path / "exp.png"
    ok = experiment.write_scatter(cells, out)
    if ok:
        assert out.is_file()
        assert out.stat().st_size > 0
    else:
        assert not out.exists()


def test_quick_main_run(experiment: ModuleType, tmp_path: Path) -> None:
    """Run main() with --quick to ensure the full CLI path works."""
    json_path = tmp_path / "quick.json"
    png_path = tmp_path / "quick.png"
    rc = experiment.main(
        [
            "--quick",
            "--length", "400",
            "--json-output", str(json_path),
            "--png-output", str(png_path),
            "--no-plot",
        ]
    )
    assert rc == 0
    assert json_path.is_file()
    parsed = json.loads(json_path.read_text(encoding="utf-8"))
    # quick = 3 × 3 × 3 = 27 cells
    assert len(parsed["raw_cells"]) == 27


def test_p_env_zero_recovers_high_correlation(experiment: ModuleType) -> None:
    """Sanity: at p_env=0 the original |r|≈high regime should appear.

    Sweep only along p_noise (single driver) → r should be high.
    """
    cells = experiment.run_sweep(
        period=4, alphabet=4, length=2000,
        p_noise_values=(0.1, 0.3, 0.5, 0.7, 0.9),
        p_env_values=(0.0,),
        n_seeds=4,
    )
    result = experiment.analyse(cells)
    assert result["global_pearson"] is not None
    assert result["global_pearson"] > 0.5  # single-driver regime stays correlated
