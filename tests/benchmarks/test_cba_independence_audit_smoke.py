"""Smoke tests for ``examples/cba_independence_audit.py``.

The script lives outside the installable package, so it is loaded as
a module via ``importlib`` from its source path. We exercise the
correlation utilities on synthetic data and the round-trip from a
small in-memory CSV to ``analyse`` / ``write_json``.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest


def _load_audit() -> ModuleType:
    repo_root = Path(__file__).resolve().parents[2]
    src_path = repo_root / "examples" / "cba_independence_audit.py"
    spec = importlib.util.spec_from_file_location("cba_independence_audit", src_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load audit script at {src_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["cba_independence_audit"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def audit() -> ModuleType:
    return _load_audit()


def test_pearson_matches_numpy(audit: ModuleType) -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=200)
    y = 0.5 * x + 0.5 * rng.normal(size=200)
    expected = float(np.corrcoef(x, y)[0, 1])
    assert audit.pearson(x, y) == pytest.approx(expected, abs=1e-9)


def test_pearson_returns_nan_for_constant_input(audit: ModuleType) -> None:
    x = np.zeros(50)
    y = np.arange(50, dtype=float)
    assert np.isnan(audit.pearson(x, y))


def test_partial_pearson_zero_when_only_common_driver(audit: ModuleType) -> None:
    """If x and y are independent given z, partial r ≈ 0."""
    rng = np.random.default_rng(1)
    z = rng.normal(size=400)
    x = z + rng.normal(scale=0.3, size=400)
    y = z + rng.normal(scale=0.3, size=400)
    # global r should be high; partial controlling for z should be low
    r_global = audit.pearson(x, y)
    r_partial = audit.partial_pearson(x, y, z)
    assert r_global > 0.7
    assert abs(r_partial) < 0.3


def test_partial_pearson_preserves_real_coupling(audit: ModuleType) -> None:
    """If x and y share a coupling beyond z, partial r stays finite."""
    rng = np.random.default_rng(2)
    z = rng.normal(size=400)
    shared = rng.normal(size=400)
    x = z + shared + rng.normal(scale=0.1, size=400)
    y = z + shared + rng.normal(scale=0.1, size=400)
    r_partial = audit.partial_pearson(x, y, z)
    assert r_partial > 0.7


def test_load_promised_rows_and_analyse(audit: ModuleType, tmp_path: Path) -> None:
    csv_path = tmp_path / "mini.csv"
    fields = [
        "class", "params", "seed", "closure", "memory",
        "constraint", "persistence", "coherence", "quadrant", "notes",
    ]
    rows_data = [
        # PromisedCycle random_noise sweep
        ("PromisedCycle", "period=4,alphabet=4,p_noise=0.0", 0,
         "1.0", "1.0", "", "1.0", "1.0", "autopoietic", ""),
        ("PromisedCycle", "period=4,alphabet=4,p_noise=0.5", 0,
         "0.5", "1.0", "", "1.0", "0.5", "autopoietic", ""),
        ("PromisedCycle", "period=4,alphabet=4,p_noise=1.0", 0,
         "0.05", "1.0", "", "1.0", "0.0", "turbulence", ""),
        # adversarial
        ("PromisedCycle", "adversarial,period=4", 0,
         "1.0", "1.0", "", "1.0", "1.0", "autopoietic", ""),
        # ECA must be filtered out
        ("ECASystem", "rule=110", 0,
         "0.7", "0.6", "1.0", "0.3", "", "autopoietic", ""),
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(fields)
        writer.writerows(rows_data)

    rows = audit.load_promised_rows(csv_path)
    assert len(rows) == 4
    modes = {r.mode for r in rows}
    assert modes == {"random_noise", "adversarial_shift"}

    result = audit.analyse(rows)
    assert result["n_total"] == 4
    assert result["n_random_noise"] == 3
    assert result["n_adversarial"] == 1
    assert "closure-coherence" in result["global_correlations"]


def test_write_json_round_trip(audit: ModuleType, tmp_path: Path) -> None:
    rows = [
        audit.PromisedRow(
            period=4, alphabet=4, p_noise=0.0, seed=0,
            closure=1.0, memory=1.0, persistence=1.0,
            coherence=1.0, mode="random_noise",
        ),
        audit.PromisedRow(
            period=4, alphabet=4, p_noise=1.0, seed=0,
            closure=0.0, memory=1.0, persistence=1.0,
            coherence=0.0, mode="random_noise",
        ),
    ]
    result = audit.analyse(rows)
    out = tmp_path / "audit.json"
    audit.write_json(result, out)
    parsed = json.loads(out.read_text(encoding="utf-8"))
    assert parsed["n_total"] == 2
    assert "global_correlations" in parsed


def test_write_scatter_runs_or_skips_cleanly(
    audit: ModuleType, tmp_path: Path
) -> None:
    rows = [
        audit.PromisedRow(
            period=4, alphabet=4, p_noise=p, seed=0,
            closure=1.0 - p, memory=1.0, persistence=1.0,
            coherence=1.0 - p, mode="random_noise",
        )
        for p in (0.0, 0.25, 0.5, 0.75, 1.0)
    ]
    out = tmp_path / "audit.png"
    ok = audit.write_scatter(rows, out)
    if ok:
        assert out.is_file()
        assert out.stat().st_size > 0
    else:
        assert not out.exists()
