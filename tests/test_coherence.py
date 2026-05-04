"""Unit tests for ``compute_cba_theil_u`` and the CBA module."""

from __future__ import annotations

import numpy as np
import pytest

from autonometrics.metrics import compute_cba_theil_u


def test_identical_trajectories_score_one() -> None:
    rng = np.random.default_rng(0)
    d = rng.integers(0, 4, size=512).astype(np.int64)
    e = d.copy()
    score = compute_cba_theil_u(d, e)
    assert score == pytest.approx(1.0, abs=1e-6)


def test_independent_trajectories_score_low() -> None:
    rng = np.random.default_rng(1)
    d = rng.integers(0, 4, size=2000).astype(np.int64)
    e = rng.integers(0, 4, size=2000).astype(np.int64)
    score = compute_cba_theil_u(d, e)
    assert score < 0.05


def test_constant_declared_returns_zero() -> None:
    rng = np.random.default_rng(2)
    d = np.zeros(256, dtype=np.int64)
    e = rng.integers(0, 4, size=256).astype(np.int64)
    score = compute_cba_theil_u(d, e)
    assert score == 0.0


def test_systematic_bijection_high_theil_low_match() -> None:
    """Textbook case: ``E = (D + 1) mod m`` predicts perfectly but never matches."""
    rng = np.random.default_rng(3)
    d = rng.integers(0, 5, size=512).astype(np.int64)
    e = ((d + 1) % 5).astype(np.int64)

    score, diagnostics = compute_cba_theil_u(d, e, return_diagnostics=True)
    assert score == pytest.approx(1.0, abs=1e-6)
    assert diagnostics["match_rate"] == pytest.approx(0.0, abs=1e-9)


def test_partial_coupling_intermediate_score() -> None:
    """Half the executed trajectory copies declared, half is random → mid score."""
    rng = np.random.default_rng(4)
    d = rng.integers(0, 4, size=2000).astype(np.int64)
    flip = rng.random(2000) < 0.5
    noise = rng.integers(0, 4, size=2000).astype(np.int64)
    e = np.where(flip, noise, d).astype(np.int64)

    score = compute_cba_theil_u(d, e)
    assert 0.15 < score < 0.85


def test_shape_mismatch_raises() -> None:
    d = np.array([0, 1, 0, 1], dtype=np.int64)
    e = np.array([0, 1, 0], dtype=np.int64)
    with pytest.raises(ValueError, match="same shape"):
        compute_cba_theil_u(d, e)


def test_non_integer_dtype_raises() -> None:
    d = np.linspace(0.0, 1.0, num=100)
    e = np.linspace(0.0, 1.0, num=100)
    with pytest.raises(ValueError, match="integer-valued"):
        compute_cba_theil_u(d, e)


def test_empty_input_raises() -> None:
    d = np.array([], dtype=np.int64)
    e = np.array([], dtype=np.int64)
    with pytest.raises(ValueError, match="non-empty"):
        compute_cba_theil_u(d, e)


def test_non_one_dimensional_raises() -> None:
    d = np.zeros((10, 10), dtype=np.int64)
    e = np.zeros((10, 10), dtype=np.int64)
    with pytest.raises(ValueError, match="1-D"):
        compute_cba_theil_u(d, e)


def test_low_n_emits_runtime_warning() -> None:
    rng = np.random.default_rng(5)
    d = rng.integers(0, 3, size=20).astype(np.int64)
    e = rng.integers(0, 3, size=20).astype(np.int64)
    with pytest.warns(RuntimeWarning, match="< 100"):
        compute_cba_theil_u(d, e)


def test_above_threshold_no_warning() -> None:
    rng = np.random.default_rng(6)
    d = rng.integers(0, 3, size=200).astype(np.int64)
    e = rng.integers(0, 3, size=200).astype(np.int64)
    with warnings_as_errors():
        compute_cba_theil_u(d, e)


def test_reproducibility() -> None:
    rng = np.random.default_rng(7)
    d = rng.integers(0, 3, size=500).astype(np.int64)
    e = rng.integers(0, 3, size=500).astype(np.int64)
    s1 = compute_cba_theil_u(d, e)
    s2 = compute_cba_theil_u(d, e)
    assert s1 == s2


def test_diagnostics_contract() -> None:
    rng = np.random.default_rng(8)
    d = rng.integers(0, 4, size=512).astype(np.int64)
    e = d.copy()
    score, diagnostics = compute_cba_theil_u(d, e, return_diagnostics=True)
    assert isinstance(score, float)
    assert isinstance(diagnostics, dict)
    assert set(diagnostics.keys()) == {"match_rate", "H_D", "H_E", "MI", "T"}
    assert diagnostics["match_rate"] == pytest.approx(1.0)
    assert diagnostics["T"] == 512
    assert diagnostics["MI"] == pytest.approx(diagnostics["H_D"], abs=1e-6)


def test_alphabet_invariance() -> None:
    """Score is invariant under alphabet relabelling on either side."""
    rng = np.random.default_rng(9)
    d = rng.integers(0, 4, size=512).astype(np.int64)
    flip = rng.random(512) < 0.3
    noise = rng.integers(0, 4, size=512).astype(np.int64)
    e = np.where(flip, noise, d).astype(np.int64)

    s_original = compute_cba_theil_u(d, e)

    relabel_d = np.array([7, 11, 19, 23], dtype=np.int64)
    relabel_e = np.array([100, 200, 300, 400], dtype=np.int64)
    d2 = relabel_d[d]
    e2 = relabel_e[e]
    s_relabeled = compute_cba_theil_u(d2, e2)

    assert s_original == pytest.approx(s_relabeled, abs=1e-9)


def test_coherence_does_not_import_other_metrics() -> None:
    """Audit: coherence module is information-theory-toolkit-free and graph-free."""
    import autonometrics.metrics.coherence as mod

    src = open(mod.__file__, encoding="utf-8").read()
    assert "from autonometrics.metrics._entropy" not in src
    assert "import autonometrics.metrics._entropy" not in src
    assert "from autonometrics.metrics.albantakis" not in src
    assert "from autonometrics.metrics.memory_ratio" not in src
    assert "from autonometrics.metrics.constraint_closure" not in src
    assert "from autonometrics.metrics.persistence" not in src
    assert "import pyinform" not in src
    assert "import dit" not in src


class warnings_as_errors:
    """Context manager that promotes any warning to an error for the body."""

    def __enter__(self) -> None:
        import warnings as _w

        self._cm = _w.catch_warnings()
        self._cm.__enter__()
        _w.simplefilter("error")

    def __exit__(self, *exc_info) -> None:
        self._cm.__exit__(*exc_info)
