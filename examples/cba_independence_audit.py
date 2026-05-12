"""CBA × closure independence audit — Session B step 5/6 of v0.8.0a0.

Reads a benchmark CSV produced by ``examples/benchmark_demo.py`` and
runs a **diagnostic audit** of the headline finding from Session B
step 4: ``|r(closure, coherence)| = +0.96`` on the 240 PromisedCycle
rows.

The audit applies three lenses, all from existing data, all with
zero new adapter code:

1. **Stratified pairwise correlations.** The ``r`` is recomputed
   inside each individual ``(period, alphabet, p_noise)`` cell of
   the PromisedCycle sweep, so the global figure is decomposed
   into within-cell figures. If the within-cell correlations are
   small while the global one is large, the global figure is a
   between-cell artefact (the noise gradient is the only common
   driver).
2. **Partial correlation controlling for p_noise.** Standard
   formula ``r(X, Y | Z) = (r_xy - r_xz r_yz) / sqrt((1-r_xz²)(1-r_yz²))``
   with ``Z = p_noise``. If the partial correlation is near zero
   the two axes were communicating only through ``p_noise``; if
   it is still high there is structural coupling beyond the
   noise gradient.
3. **Scatter visualisation by p_noise level.** Each PromisedCycle
   point is plotted in the (closure, coherence) plane and coloured
   by its ``p_noise``. Tight per-colour bands with global
   alignment confirm a between-cluster correlation; per-colour
   scatter with global alignment indicates within-cluster
   independence.

The audit does **not** apply any decision threshold itself; it
only computes the indicators. The verdict step (does the hard
gate from ``docs/CBA.md`` apply or get overridden?) is performed
in the documentation phase.

Outputs:

- a human-readable report on stdout,
- a structured JSON snapshot at
  ``docs/benchmarks/cba_independence_v0.8.0a0.json``,
- a scatter PNG at
  ``docs/benchmarks/cba_independence_v0.8.0a0.png`` (only when
  matplotlib is available; the analysis is independent of the
  plot).

Usage::

    python examples/cba_independence_audit.py
    python examples/cba_independence_audit.py --csv path/to/run.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

_PROMISED_PATTERN = re.compile(
    r"period=(?P<period>\d+),alphabet=(?P<alphabet>\d+),p_noise=(?P<p_noise>[\d.]+)"
)


@dataclass
class PromisedRow:
    """A single PromisedCycle benchmark row with the four numeric axes parsed."""

    period: int
    alphabet: int
    p_noise: float
    seed: int
    closure: float | None
    memory: float | None
    persistence: float | None
    coherence: float | None
    mode: str  # "random_noise" or "adversarial_shift"


def _maybe_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def load_promised_rows(path: Path) -> list[PromisedRow]:
    """Return only the PromisedCycle rows from a five-axis benchmark CSV."""
    rows: list[PromisedRow] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            if raw.get("class") != "PromisedCycle":
                continue
            params = raw.get("params", "")
            seed = int(raw["seed"])
            closure = _maybe_float(raw.get("closure"))
            memory = _maybe_float(raw.get("memory"))
            persistence = _maybe_float(raw.get("persistence"))
            coherence = _maybe_float(raw.get("coherence"))

            if params.startswith("adversarial"):
                m = re.search(r"period=(?P<period>\d+)", params)
                period = int(m.group("period")) if m else 0
                rows.append(
                    PromisedRow(
                        period=period,
                        alphabet=0,  # adversarial uses alphabet=period+1; not required
                        p_noise=float("nan"),
                        seed=seed,
                        closure=closure,
                        memory=memory,
                        persistence=persistence,
                        coherence=coherence,
                        mode="adversarial_shift",
                    )
                )
                continue

            m = _PROMISED_PATTERN.search(params)
            if not m:
                continue
            rows.append(
                PromisedRow(
                    period=int(m.group("period")),
                    alphabet=int(m.group("alphabet")),
                    p_noise=float(m.group("p_noise")),
                    seed=seed,
                    closure=closure,
                    memory=memory,
                    persistence=persistence,
                    coherence=coherence,
                    mode="random_noise",
                )
            )
    return rows


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 2 or y.size < 2:
        return float("nan")
    if np.std(x) <= 0 or np.std(y) <= 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 2:
        return float("nan")
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return pearson(rx, ry)


def partial_pearson(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float:
    """Partial Pearson correlation of x and y controlling for z.

    Returns ``nan`` when the sample is too small or when one of the
    pairwise correlations against ``z`` saturates at ``±1`` (the
    denominator collapses).
    """
    if x.size < 3:
        return float("nan")
    r_xy = pearson(x, y)
    r_xz = pearson(x, z)
    r_yz = pearson(y, z)
    for r in (r_xy, r_xz, r_yz):
        if np.isnan(r):
            return float("nan")
    denom = np.sqrt((1.0 - r_xz**2) * (1.0 - r_yz**2))
    if denom <= 1e-12:
        return float("nan")
    return float((r_xy - r_xz * r_yz) / denom)


def _valid_pair(
    rows: list[PromisedRow], a: str, b: str
) -> tuple[np.ndarray, np.ndarray, list[PromisedRow]]:
    """Return paired arrays (a, b) for rows where both are not None."""
    xs: list[float] = []
    ys: list[float] = []
    selected: list[PromisedRow] = []
    for r in rows:
        va = getattr(r, a)
        vb = getattr(r, b)
        if va is None or vb is None:
            continue
        xs.append(float(va))
        ys.append(float(vb))
        selected.append(r)
    return np.asarray(xs, dtype=float), np.asarray(ys, dtype=float), selected


def stratified_correlations(rows: list[PromisedRow], a: str, b: str) -> list[dict[str, Any]]:
    """Per-cell ``r(a, b)`` for each (period, alphabet, p_noise) cell.

    Adversarial rows are reported under their own dedicated cell.
    Cells with fewer than 2 valid pairs are returned with ``nan``.
    """
    cells: dict[tuple[str, int, int, float], list[PromisedRow]] = defaultdict(list)
    for r in rows:
        if r.mode == "adversarial_shift":
            key = ("adversarial", r.period, 0, float("nan"))
        else:
            key = ("random_noise", r.period, r.alphabet, r.p_noise)
        cells[key].append(r)

    out: list[dict[str, Any]] = []
    for key, members in sorted(cells.items(), key=_cell_sort_key):
        x, y, _ = _valid_pair(members, a, b)
        n = int(x.size)
        out.append(
            {
                "mode": key[0],
                "period": int(key[1]),
                "alphabet": int(key[2]),
                "p_noise": (
                    None if isinstance(key[3], float) and np.isnan(key[3]) else float(key[3])
                ),
                "n": n,
                "pearson": pearson(x, y) if n >= 2 else float("nan"),
                "spearman": spearman(x, y) if n >= 2 else float("nan"),
            }
        )
    return out


def _cell_sort_key(item: tuple[Any, list[PromisedRow]]) -> tuple[int, int, int, float]:
    key, _ = item
    mode_rank = 0 if key[0] == "random_noise" else 1
    p = key[3] if not (isinstance(key[3], float) and np.isnan(key[3])) else 99.0
    return (mode_rank, int(key[1]), int(key[2]), float(p))


def global_pair_summary(rows: list[PromisedRow], a: str, b: str) -> dict[str, Any]:
    """Return overall and partial-controlled correlations for one pair."""
    x, y, selected = _valid_pair(rows, a, b)
    n = int(x.size)

    p_noise = np.array([r.p_noise for r in selected if not np.isnan(r.p_noise)], dtype=float)
    has_p_noise = p_noise.size == n  # only valid for random_noise rows

    return {
        "n": n,
        "pearson": pearson(x, y) if n >= 2 else float("nan"),
        "spearman": spearman(x, y) if n >= 2 else float("nan"),
        "partial_pearson_controlling_p_noise": (
            partial_pearson(x, y, p_noise) if has_p_noise and n >= 3 else float("nan")
        ),
        "n_random_noise": int(p_noise.size),
    }


def analyse(rows: list[PromisedRow]) -> dict[str, Any]:
    """Run the full audit on the PromisedCycle subset."""
    random_noise_rows = [r for r in rows if r.mode == "random_noise"]
    adversarial_rows = [r for r in rows if r.mode == "adversarial_shift"]

    pairs = (
        ("closure", "coherence"),
        ("closure", "memory"),
        ("closure", "persistence"),
        ("memory", "coherence"),
        ("persistence", "coherence"),
        ("memory", "persistence"),
    )

    pair_globals = {f"{a}-{b}": global_pair_summary(rows, a, b) for a, b in pairs}
    pair_random = {f"{a}-{b}": global_pair_summary(random_noise_rows, a, b) for a, b in pairs}

    stratified = {f"{a}-{b}": stratified_correlations(rows, a, b) for a, b in pairs}

    return {
        "n_total": len(rows),
        "n_random_noise": len(random_noise_rows),
        "n_adversarial": len(adversarial_rows),
        "global_correlations": pair_globals,
        "random_noise_correlations": pair_random,
        "stratified_correlations": stratified,
    }


def _fmt(value: float | None) -> str:
    if value is None:
        return "  n/a"
    if isinstance(value, float) and np.isnan(value):
        return "  n/a"
    return f"{value:+.4f}"


def print_report(result: dict[str, Any]) -> None:
    print("CBA × closure independence audit (v0.8.0a0)")
    print("=" * 64)
    print()
    print(
        f"PromisedCycle rows: {result['n_total']} "
        f"(random_noise: {result['n_random_noise']}, "
        f"adversarial: {result['n_adversarial']})"
    )
    print()
    print("--- Global pairwise (all PromisedCycle rows) ---")
    print(f"  {'pair':<24} {'n':>4} {'pearson':>10} {'spearman':>10} {'partial|p':>11}")
    print(f"  {'-' * 24} {'-' * 4} {'-' * 10} {'-' * 10} {'-' * 11}")
    for name, stats in result["global_correlations"].items():
        print(
            f"  {name:<24} {stats['n']:>4} "
            f"{_fmt(stats['pearson']):>10} "
            f"{_fmt(stats['spearman']):>10} "
            f"{_fmt(stats['partial_pearson_controlling_p_noise']):>11}"
        )
    print()
    print("--- Random-noise mode only (adversarial excluded) ---")
    print(f"  {'pair':<24} {'n':>4} {'pearson':>10} {'spearman':>10} {'partial|p':>11}")
    print(f"  {'-' * 24} {'-' * 4} {'-' * 10} {'-' * 10} {'-' * 11}")
    for name, stats in result["random_noise_correlations"].items():
        print(
            f"  {name:<24} {stats['n']:>4} "
            f"{_fmt(stats['pearson']):>10} "
            f"{_fmt(stats['spearman']):>10} "
            f"{_fmt(stats['partial_pearson_controlling_p_noise']):>11}"
        )
    print()
    print("--- Stratified by (period, alphabet, p_noise) ---")
    for pair_name, cells in result["stratified_correlations"].items():
        print(f"  pair: {pair_name}")
        print(
            f"    {'mode':<16} {'period':>6} {'alpha':>5} {'p_noise':>8} "
            f"{'n':>4} {'pearson':>10} {'spearman':>10}"
        )
        print(f"    {'-' * 16} {'-' * 6} {'-' * 5} {'-' * 8} {'-' * 4} {'-' * 10} {'-' * 10}")
        for cell in cells:
            p_noise_str = "  n/a" if cell["p_noise"] is None else f"{cell['p_noise']:.2f}"
            print(
                f"    {cell['mode']:<16} {cell['period']:>6} {cell['alphabet']:>5} "
                f"{p_noise_str:>8} {cell['n']:>4} "
                f"{_fmt(cell['pearson']):>10} {_fmt(cell['spearman']):>10}"
            )
        print()
    print("Thresholds and verdict are NOT applied here.")
    print("See docs/CBA.md to interpret these numbers.")


def write_json(result: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    def _convert(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {str(k): _convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_convert(v) for v in obj]
        if isinstance(obj, tuple):
            return [_convert(v) for v in obj]
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, float) and np.isnan(obj):
            return None
        return obj

    with path.open("w", encoding="utf-8") as fh:
        json.dump(_convert(result), fh, indent=2, ensure_ascii=False)


def write_scatter(rows: list[PromisedRow], path: Path) -> bool:
    """Save a (closure, coherence) scatter coloured by p_noise.

    Returns ``True`` on success, ``False`` if matplotlib is not
    available. Adversarial rows are marked with a dedicated symbol.
    """
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    random_rows = [
        r
        for r in rows
        if r.mode == "random_noise" and r.closure is not None and r.coherence is not None
    ]
    adversarial_rows = [
        r
        for r in rows
        if r.mode == "adversarial_shift" and r.closure is not None and r.coherence is not None
    ]

    fig, ax = plt.subplots(figsize=(7.5, 6.5))

    if random_rows:
        x = np.array([r.closure for r in random_rows], dtype=float)
        y = np.array([r.coherence for r in random_rows], dtype=float)
        c = np.array([r.p_noise for r in random_rows], dtype=float)
        sc = ax.scatter(x, y, c=c, cmap="viridis", s=42, alpha=0.85, edgecolors="none")
        cbar = fig.colorbar(sc, ax=ax)
        cbar.set_label("p_noise")

    if adversarial_rows:
        x = np.array([r.closure for r in adversarial_rows], dtype=float)
        y = np.array([r.coherence for r in adversarial_rows], dtype=float)
        ax.scatter(
            x,
            y,
            facecolors="none",
            edgecolors="red",
            s=80,
            marker="D",
            linewidths=1.5,
            label="adversarial_shift",
        )
        ax.legend(loc="lower right", framealpha=0.9)

    ax.plot([0, 1], [0, 1], color="grey", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.set_xlabel("closure (ratio_endo_total)")
    ax.set_ylabel("coherence (cba_theil_u)")
    ax.set_title(
        "PromisedCycle: closure × coherence by p_noise\n"
        "(diagnostic for the |r|=0.96 finding in Session B)"
    )
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return True


_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_CSV = _REPO_ROOT / "docs" / "benchmarks" / "v0.8.0a0.csv"
_DEFAULT_JSON = _REPO_ROOT / "docs" / "benchmarks" / "cba_independence_v0.8.0a0.json"
_DEFAULT_PNG = _REPO_ROOT / "docs" / "benchmarks" / "cba_independence_v0.8.0a0.png"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="CBA × closure independence audit for autonometrics."
    )
    parser.add_argument("--csv", type=Path, default=_DEFAULT_CSV)
    parser.add_argument("--json-output", type=Path, default=_DEFAULT_JSON)
    parser.add_argument("--png-output", type=Path, default=_DEFAULT_PNG)
    parser.add_argument("--no-plot", action="store_true", help="Skip the scatter PNG output.")
    args = parser.parse_args(argv)

    if not args.csv.is_file():
        parser.error(f"CSV not found: {args.csv}")

    rows = load_promised_rows(args.csv)
    if not rows:
        parser.error(f"No PromisedCycle rows in {args.csv}; nothing to audit.")
    result = analyse(rows)
    print_report(result)
    write_json(result, args.json_output)
    print(f"\nJSON saved to: {args.json_output}")

    if args.no_plot:
        return 0
    if write_scatter(rows, args.png_output):
        print(f"PNG saved to:  {args.png_output}")
    else:
        print("matplotlib not available; scatter PNG skipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
