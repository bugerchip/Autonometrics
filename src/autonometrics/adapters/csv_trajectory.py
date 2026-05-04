"""CSV-backed adapter for user-supplied discrete trajectories.

This adapter is the minimum-viable bridge between real-world data and
the :class:`autonometrics.Autonometer`. The user is responsible for
discretising their signal upstream; the adapter only handles IO and
shape validation.

The CSV is expected to contain two integer columns, by default named
``state`` and ``env``. A header is optional: the first row is treated
as a header when at least one cell fails to parse as an integer.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np


class CSVTrajectory:
    """Adapter wrapping a two-column CSV of discrete ``(state, env)`` pairs."""

    def __init__(self, state: np.ndarray, env: np.ndarray) -> None:
        state_arr = np.asarray(state).ravel()
        env_arr = np.asarray(env).ravel()

        if state_arr.shape != env_arr.shape:
            raise ValueError(
                f"state and env must have the same length: "
                f"got {state_arr.shape[0]} and {env_arr.shape[0]}"
            )
        if state_arr.size < 2:
            raise ValueError(f"trajectory must contain at least 2 rows; got {state_arr.size}")
        if not np.issubdtype(state_arr.dtype, np.integer):
            raise ValueError(f"state column must be integer-valued; got dtype {state_arr.dtype}")
        if not np.issubdtype(env_arr.dtype, np.integer):
            raise ValueError(f"env column must be integer-valued; got dtype {env_arr.dtype}")

        self._state = state_arr.astype(np.int64, copy=False)
        self._env = env_arr.astype(np.int64, copy=False)

    @classmethod
    def from_arrays(cls, state: np.ndarray, env: np.ndarray) -> CSVTrajectory:
        """Build a trajectory directly from two arrays, no disk IO."""
        return cls(state=state, env=env)

    @classmethod
    def from_file(
        cls,
        path: str | Path,
        state_col: str = "state",
        env_col: str = "env",
    ) -> CSVTrajectory:
        """Load a trajectory from a CSV file.

        Canonical entry point since v0.8.2a0; matches the
        ``from_file`` / ``read_csv`` naming convention used by pandas,
        numpy and most of the scientific Python ecosystem. The legacy
        :meth:`from_path` alias remains supported indefinitely.

        Parameters
        ----------
        path:
            File system path to the CSV.
        state_col, env_col:
            Column names for the system state and the environment.
            When the file has no header, ``"state"`` and ``"env"`` are
            mapped to columns ``0`` and ``1`` respectively; any other
            name without a header raises ``ValueError``.
        """
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"CSV not found: {p}")

        with p.open("r", encoding="utf-8", newline="") as fh:
            rows = [row for row in csv.reader(fh) if row]

        if not rows:
            raise ValueError(f"CSV file is empty: {p}")

        first_row = rows[0]
        if len(first_row) < 2:
            raise ValueError(f"CSV must have at least two columns; first row has {len(first_row)}")

        has_header = not _row_is_integer(first_row)
        if has_header:
            header = [cell.strip() for cell in first_row]
            body = rows[1:]
            col_index = {name: i for i, name in enumerate(header)}
            if state_col not in col_index:
                raise ValueError(f"state column {state_col!r} not found in header {header}")
            if env_col not in col_index:
                raise ValueError(f"env column {env_col!r} not found in header {header}")
            state_idx = col_index[state_col]
            env_idx = col_index[env_col]
        else:
            body = rows
            default_positions = {"state": 0, "env": 1}
            if state_col not in default_positions:
                raise ValueError(f"CSV has no header; state_col must be 'state', got {state_col!r}")
            if env_col not in default_positions:
                raise ValueError(f"CSV has no header; env_col must be 'env', got {env_col!r}")
            state_idx = default_positions[state_col]
            env_idx = default_positions[env_col]

        if not body:
            raise ValueError(f"CSV has no data rows: {p}")

        state_vals: list[int] = []
        env_vals: list[int] = []
        for i, row in enumerate(body, start=2 if has_header else 1):
            if len(row) <= max(state_idx, env_idx):
                raise ValueError(
                    f"row {i} has {len(row)} columns, expected at least "
                    f"{max(state_idx, env_idx) + 1}"
                )
            try:
                state_vals.append(int(row[state_idx]))
                env_vals.append(int(row[env_idx]))
            except ValueError as exc:
                raise ValueError(f"non-integer value at row {i}: {row!r}") from exc

        return cls(
            state=np.asarray(state_vals, dtype=np.int64),
            env=np.asarray(env_vals, dtype=np.int64),
        )

    @classmethod
    def from_path(
        cls,
        path: str | Path,
        state_col: str = "state",
        env_col: str = "env",
    ) -> CSVTrajectory:
        """Legacy alias of :meth:`from_file`, kept for backward compatibility.

        ``from_path`` was the original entry point in versions
        ``v0.1.0`` through ``v0.8.1a0``. Since ``v0.8.2a0`` the
        canonical name is :meth:`from_file`, which matches the
        ecosystem convention (``pandas.read_csv``, ``np.loadtxt``,
        ``json.load``, ...). This alias delegates to
        :meth:`from_file` unchanged and will remain supported until
        at least ``v2.0``.
        """
        return cls.from_file(path=path, state_col=state_col, env_col=env_col)

    def get_state_history(self) -> np.ndarray:
        return self._state.copy()

    def get_env_history(self) -> np.ndarray:
        return self._env.copy()


def _row_is_integer(row: list[str]) -> bool:
    """Return ``True`` when every cell in ``row`` parses as an integer."""
    for cell in row:
        try:
            int(cell.strip())
        except ValueError:
            return False
    return True
