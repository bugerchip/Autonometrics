"""Tests for the CSVTrajectory adapter."""

from pathlib import Path

import numpy as np
import pytest

from autonometrics import Autonometer, CSVTrajectory, SimpleAutomaton


def _write_csv(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_from_arrays_preserves_data() -> None:
    state = np.array([0, 1, 2, 1, 0], dtype=np.int64)
    env = np.array([1, 0, 0, 1, 1], dtype=np.int64)
    traj = CSVTrajectory.from_arrays(state=state, env=env)
    np.testing.assert_array_equal(traj.get_state_history(), state)
    np.testing.assert_array_equal(traj.get_env_history(), env)


def test_from_arrays_rejects_non_integer_dtype() -> None:
    state = np.array([0.1, 1.0, 2.0])
    env = np.array([1.0, 0.0, 1.0])
    with pytest.raises(ValueError, match="integer-valued"):
        CSVTrajectory.from_arrays(state=state, env=env)


def test_from_arrays_rejects_length_mismatch() -> None:
    with pytest.raises(ValueError, match="same length"):
        CSVTrajectory.from_arrays(
            state=np.array([0, 1, 0], dtype=np.int64),
            env=np.array([1, 0], dtype=np.int64),
        )


def test_from_arrays_rejects_too_short() -> None:
    with pytest.raises(ValueError, match="at least 2 rows"):
        CSVTrajectory.from_arrays(
            state=np.array([0], dtype=np.int64),
            env=np.array([1], dtype=np.int64),
        )


def test_from_path_with_header(tmp_path: Path) -> None:
    csv_path = _write_csv(
        tmp_path / "traj.csv",
        "state,env\n0,1\n2,1\n2,0\n1,0\n",
    )
    traj = CSVTrajectory.from_path(csv_path)
    np.testing.assert_array_equal(traj.get_state_history(), [0, 2, 2, 1])
    np.testing.assert_array_equal(traj.get_env_history(), [1, 1, 0, 0])


def test_from_path_without_header(tmp_path: Path) -> None:
    csv_path = _write_csv(tmp_path / "traj.csv", "0,1\n2,1\n2,0\n1,0\n")
    traj = CSVTrajectory.from_path(csv_path)
    np.testing.assert_array_equal(traj.get_state_history(), [0, 2, 2, 1])
    np.testing.assert_array_equal(traj.get_env_history(), [1, 1, 0, 0])


def test_from_path_column_order_can_be_swapped(tmp_path: Path) -> None:
    csv_path = _write_csv(
        tmp_path / "traj.csv",
        "a,b\n0,1\n2,1\n2,0\n1,0\n",
    )
    traj = CSVTrajectory.from_path(csv_path, state_col="b", env_col="a")
    np.testing.assert_array_equal(traj.get_state_history(), [1, 1, 0, 0])
    np.testing.assert_array_equal(traj.get_env_history(), [0, 2, 2, 1])


def test_from_path_missing_column_raises(tmp_path: Path) -> None:
    csv_path = _write_csv(tmp_path / "traj.csv", "state,other\n0,1\n1,0\n")
    with pytest.raises(ValueError, match="env column 'env' not found"):
        CSVTrajectory.from_path(csv_path)


def test_from_path_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        CSVTrajectory.from_path(tmp_path / "does_not_exist.csv")


def test_from_path_single_data_row_raises(tmp_path: Path) -> None:
    csv_path = _write_csv(tmp_path / "traj.csv", "state,env\n0,1\n")
    with pytest.raises(ValueError, match="at least 2 rows"):
        CSVTrajectory.from_path(csv_path)


def test_from_path_non_integer_value_raises(tmp_path: Path) -> None:
    csv_path = _write_csv(tmp_path / "traj.csv", "state,env\n0,1\n1,abc\n")
    with pytest.raises(ValueError, match="non-integer value"):
        CSVTrajectory.from_path(csv_path)


def test_from_path_unknown_column_without_header_raises(tmp_path: Path) -> None:
    csv_path = _write_csv(tmp_path / "traj.csv", "0,1\n1,0\n")
    with pytest.raises(ValueError, match="CSV has no header"):
        CSVTrajectory.from_path(csv_path, state_col="foo")


def test_roundtrip_through_csv_matches_direct_measurement(tmp_path: Path) -> None:
    """Write a SimpleAutomaton trajectory to CSV, reload it, and compare scores."""
    rng = np.random.default_rng(0)
    env = rng.integers(0, 3, size=2000).astype(np.int64)
    auto = SimpleAutomaton.from_self_generated_rules(n_states=4, env=env, seed=0)

    state_history = auto.get_state_history()
    env_history = auto.get_env_history()

    csv_path = tmp_path / "traj.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        fh.write("state,env\n")
        for s, e in zip(state_history, env_history, strict=True):
            fh.write(f"{int(s)},{int(e)}\n")

    traj = CSVTrajectory.from_path(csv_path)

    meter = Autonometer(metrics=["albantakis", "memory"])
    profile_direct = meter.measure(auto)
    profile_csv = meter.measure(traj)

    assert profile_direct.ratio_endo_total == pytest.approx(profile_csv.ratio_endo_total)
    assert profile_direct.structural_memory == pytest.approx(profile_csv.structural_memory)
    assert profile_csv.metadata["adapter"] == "CSVTrajectory"
