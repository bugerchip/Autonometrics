# API Freeze Plan

> Status: drafted on `v0.8.1a0`. Active until `v1.0`.

This document records the canonical public API of `autonometrics`,
the rationale behind it, and the deprecation policy for the legacy
internal vocabulary that pre-dated the canonical naming.

## Motivation

Up to and including `v0.8.0a0` the package shipped **three parallel
vocabularies** for the same five autonomy axes:

| Concept (README) | Metric ID (`Autonometer`) | Profile field          | `compute_*` function          |
| :--------------- | :------------------------ | :--------------------- | :---------------------------- |
| `closure`        | `albantakis`              | `ratio_endo_total`     | `compute_albantakis`          |
| `memory`         | `memory`                  | `memory_endo_ratio`    | `compute_memory_endo_ratio`   |
| `constraint`     | `constraint_closure`      | `constraint_closure`   | `compute_constraint_closure`  |
| `persistence`    | `persistence`             | `rai_proxy_persistence`| `compute_rai_proxy_persistence`|
| `coherence`      | `coherence`               | `cba_theil_u`          | `compute_cba_theil_u`         |

Out of five axes only `memory` was internally consistent. New users
opening the README and writing `Autonometer(metrics=["closure"])`
would hit `ValueError`. Users reading a result by `profile.closure`
would also fail. The cost of carrying this organic, axis-by-axis
naming into a stable `v1.0` was judged too high; `v0.8.1a0` introduces
the canonical vocabulary as the recommended access path while keeping
the legacy names alive as aliases.

## Canonical axis names (frozen since `v0.8.1a0`)

```python
import autonometrics as anm

assert anm.AXES == ("closure", "memory", "constraint", "persistence", "coherence")
assert anm.ALL_AXES is anm.AXES  # alias kept for explicitness
```

These five strings are the **only** axis names guaranteed to remain
stable through `v1.0` and forward. New code should use them
exclusively.

## Recommended public surface

```python
import autonometrics as anm

# 1. One-line measurement (recommended for applied users).
profile = anm.measure(some_adapter)

# 2. Subset of axes.
profile = anm.measure(some_adapter, axes=["closure", "coherence"])

# 3. Equivalent long form.
meter = anm.Autonometer(metrics=["closure", "coherence"])
profile = meter.measure(some_adapter)

# 4. Read results by canonical name.
profile.closure                      # property accessor
profile["coherence"]                 # dict-style accessor
profile.to_dict()                    # full canonical dictionary
profile.defined_axes()               # axes that were actually computed

# 5. Compute a single metric directly.
score = anm.compute_closure(states, env)
score = anm.compute_coherence(declared, executed)
```

## Backward-compatibility guarantees

The following legacy names continue to work in `v0.8.1a0` and remain
supported until at least `v2.0`:

* Metric identifiers: `albantakis`, `constraint_closure` (the rest are
  already canonical).
* Profile fields: `ratio_endo_total`, `memory_endo_ratio`,
  `constraint_closure`, `rai_proxy_persistence`, `cba_theil_u`.
* Functions: `compute_albantakis`, `compute_memory_endo_ratio`,
  `compute_constraint_closure`, `compute_rai_proxy_persistence`,
  `compute_cba_theil_u`.

Translation is handled internally by `_resolve_metric_name` in
`autonometrics.core` and the canonical properties on
`AutonomyProfile`. Calling code does not need to be aware of either
mechanism.

## Default behaviour change

`Autonometer()` previously defaulted to `metrics=["albantakis"]`,
which silently dropped four of the five canonical readings. Since
`v0.8.1a0` the default is `metrics=AXES`, i.e. all five canonical
axes. Adapters that do not support a given axis still report `None`
for that field (mosaic-dropout policy), so callers see at most one
extra `None` field rather than missing data.

## Deprecation timeline

| Release   | Behaviour for legacy names                                   |
| :-------- | :----------------------------------------------------------- |
| `v0.8.1a0`| Soft alias. Both legacy and canonical names work; no warning.|
| `v0.10.x` | Soft alias **with** `DeprecationWarning` on legacy names.    |
| `v1.0.0`  | Active warning continues; documentation removes legacy names.|
| `v2.0.0`  | Legacy names are removed.                                    |

The `v2.0` removal applies only to the **public** legacy names listed
above. The internal `_METRIC_REGISTRY` keys (`albantakis`,
`constraint_closure`) and the `AutonomyProfile` field names may also
be renamed at `v2.0` for consistency, but this is a downstream
implementation detail and will not affect anyone using the canonical
API documented here.

## What is **not** covered by this freeze

The following are explicitly **not** part of the frozen public surface
yet and may change without notice up to `v1.0`:

* Adapter constructors (`PromisedCycle`, `SimpleAutomaton`,
  `CSVTrajectory`, `LLMTranscriptAdapter`). Verbose constructor
  signatures may be paired with factory methods
  (`PromisedCycle.simple(...)`, `SimpleAutomaton.demo(...)`,
  `CSVTrajectory.from_file(...)`,
  `LLMTranscriptAdapter.from_jsonl(...)`,
  `LLMTranscriptAdapter.from_messages(...)`) before freeze.
* Metadata dictionary contents (`profile.metadata`). The keys
  `metric`, `metrics`, `axes`, `n_timesteps`, `adapter` are stable;
  additional keys may be added freely.
* Optional diagnostic fields on `AutonomyProfile` (added in
  `v0.9.0a1`): `cba_match_rate`, `cba_h_d`, `cba_h_e`, `cba_mi`,
  `memory_e_states`, `memory_e_env`, `persistence_mean_hamming`,
  `persistence_d_ref`. These expose intermediate magnitudes the
  underlying metrics already compute internally and follow the
  same mosaic-dropout rule as their parent axis. Their names and
  the dictionary keys returned by `return_diagnostics=True`
  (`match_rate`, `H_D`, `H_E`, `MI`, `e_states`, `e_env`,
  `mean_hamming`, `d_ref`) may be refined before `v1.0`. The
  five headline axis fields listed above remain the stable freeze
  target and are not affected.
* Internal modules: `autonometrics.core._*`, `autonometrics.metrics._*`
  and similar private members.

## Adapter-specific contracts

The Messages-format input contract for `LLMTranscriptAdapter`
(role-to-axis mapping, discretisation policy, mosaic-dropout
behaviour, multi-session handling, validation boundary) is
fixed by [`docs/LLM_TRANSCRIPT.md`](LLM_TRANSCRIPT.md), not by
this freeze. That document is the single source of truth for
what the adapter does with its input; this freeze only governs
the canonical names and the orchestrator surface. The same
separation will apply to future adapters that ship their own
domain contracts (LLM live, biological recordings, etc.).
