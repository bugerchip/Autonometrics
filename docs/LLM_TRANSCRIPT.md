# LLM Transcript Adapter — Design Contract

> Status: pre-implementation contract for `v0.9.0a0`. This
> document is the design lock that PR2–PR5 of the v0.9.0 cycle
> must follow. The adapter is not yet shipped; the contract
> below is what the code is being written against.

This document specifies the input format, the field-to-axis
mapping, the discretisation policy, the missing-data policy,
the multi-session handling, and the validation boundary for
the upcoming `LLMTranscriptAdapter`. Each decision is anchored
to a pre-existing convention in the broader scientific Python
or LLM ecosystem; nothing in this contract is invented from
scratch.

## Motivation

Up to and including `v0.8.2a0`, the only adapter that exposes
a non-trivial `declared` / `executed` distinction is
`PromisedCycle`, which is fully synthetic. The CBA (`coherence`)
axis is therefore validated mathematically but has no real-data
substrate in the package. The `v0.9.0a0` adapter closes that
gap by accepting **conversational transcripts from LLM agents**
and presenting them under the existing `AutonomySystem`
protocol.

The adapter is shipped in **off-line mode** only in `v0.9.0a0`:
it consumes already-recorded conversations. The on-line
counterpart (`LLMLiveAdapter`, capable of replaying turns with
controlled perturbations and therefore of supporting the
`persistence` axis on LLMs) is deferred to a later release.

## Input format — OpenAI / Anthropic Messages

The adapter accepts the **standard Messages format** produced
by every major LLM provider (OpenAI Chat Completions,
Anthropic Messages, the HuggingFace `chat` template). A
conversation is a list of dictionaries; each dictionary is a
turn with at least a `role` field and a `content` field.

Two equivalent persistent representations are supported:

1. **JSONL on disk**, one message per line, in any of the
   following shapes (the adapter normalises them internally):

   ```jsonc
   {"role": "user",      "content": "..."}
   {"role": "assistant", "content": "...", "tool_calls": [...]}
   {"role": "tool",      "content": "...", "tool_call_id": "..."}
   {"role": "system",    "content": "..."}
   ```

2. **In-memory `list[dict]`** with the same shape.

Both can be passed directly to the adapter:

```python
adapter = LLMTranscriptAdapter.from_jsonl("session_001.jsonl")
adapter = LLMTranscriptAdapter.from_messages(messages_list)
```

There is **no proprietary schema**. A user who already has
conversations recorded against either provider's SDK has zero
reformatting work to do.

### Optional metadata fields

The adapter ignores keys it does not understand. Recommended
optional fields that the adapter will read if present:

| Field | Purpose | Convention |
| :---- | :------ | :--------- |
| `session_id` | Group multiple conversations into a corpus | OpenTelemetry GenAI / LangSmith |
| `model` | Annotate which model produced the assistant turn | OpenAI / Anthropic API responses |
| `timestamp` | Optional ordering when a JSONL is shuffled | RFC 3339 |
| `reasoning` / `thinking` | Explicit chain-of-thought block, if surfaced | Anthropic `thinking`, OpenAI `reasoning` |

When `reasoning` / `thinking` is **not** present, the adapter
falls back to the assistant's `content` field for the
`declared` channel; see the missing-data policy below.

## Field-to-axis mapping

The protocol expects three concepts: `state`, `env`,
`declared`, `executed`. The adapter maps Messages-format roles
onto those concepts as follows:

| Concept (protocol)            | Source (Messages format)                                                | Notes |
| :---------------------------- | :---------------------------------------------------------------------- | :---- |
| `state` (i.e. executed)       | Assistant's actually-emitted action: `tool_calls[*].function.name` if any, else the assistant `content` discretised to a category | Fed to `closure`, `memory`, `persistence` (when on-line) |
| `env`                         | Concatenation of the previous `user` content and any `tool` results that arrived between the previous and current assistant turn | Fed to `closure`, `memory` |
| `declared`                    | Assistant's `reasoning` / `thinking` block if present; otherwise a parsed plan extracted from the assistant `content` ("I will…", first sentence heuristic); otherwise empty | Fed to `coherence` |
| `executed`                    | Same source as `state`                                                  | Fed to `coherence` |

The split is intentional: `state` and `executed` come from the
**same** observable action stream (an LLM has no hidden "real"
state distinct from its tool calls and replies). The
`declared` channel is the only place where the LLM's
self-reported intent enters the protocol, and it is the only
channel that can legitimately disagree with `executed`.

## Discretisation policy

The protocol expects integer arrays. The adapter follows the
**scikit-learn / pandas convention** for converting categorical
strings to integers, in three layers of decreasing automation:

1. **If the user pre-encodes the columns** as a
   `pandas.Categorical` or as `np.ndarray[int]`, the adapter
   uses the codes directly. Recommended path for power users.
2. **If the columns are strings or generic objects**, the
   adapter applies `sklearn.preprocessing.LabelEncoder`
   internally. The fitted encoder is stored on the adapter
   instance under `adapter.encoders_` so the user can inspect
   the mapping or apply it to new data.
3. **For full control**, the user passes a callable
   `to_state_id: Callable[[Any], int]`. This bypasses the
   automatic encoder entirely. Recommended for embedding-based
   discretisations or for hashing-into-a-fixed-bucket schemes.

```python
# Path 1 — pre-encoded.
df["executed"] = pd.Categorical(df["executed"])
adapter = LLMTranscriptAdapter(df)

# Path 2 — automatic LabelEncoder (default).
adapter = LLMTranscriptAdapter(df)        # df["executed"] is str

# Path 3 — user-provided callable.
adapter = LLMTranscriptAdapter(
    df,
    to_state_id=lambda action: hash(action) % 32,
)
```

The default discretisation of `executed` is one integer per
**tool call name** (`read_file`, `write`, `respond_to_user`,
`search`, etc.). Plain text replies all collapse to one
category (`respond_to_user`) unless the user overrides via
path 3. This default is conservative and predictable; it is
not the *only* sensible choice, which is exactly why path 3
exists.

## Missing-data policy (`declared` empty)

Not every assistant turn carries an explicit `declared`
channel: some models do not surface their reasoning, some
sessions are answer-only, and some providers strip the
`reasoning` block before logging. The adapter follows the
package-wide **mosaic dropout policy** already implemented in
`autonometrics.core`:

- A turn whose `declared` would be empty is **excluded** from
  the `coherence` computation, not zero-padded.
- If the *entire* corpus has no `declared` content (no
  `reasoning` field anywhere, no parseable plan in the
  assistant `content`), the adapter does **not** raise. It
  simply does not implement `get_declared_executed`, and the
  orchestrator records `None` for `coherence` in the resulting
  `AutonomyProfile` — exactly as it already does for
  `coherence` on `SimpleAutomaton` and ECAs.

This is the same convention SciPy uses (`nan` with an
informative warning when a statistic cannot be computed) and
the same convention scikit-learn uses
(`UndefinedMetricWarning`). The user gets a partial profile
and a clear message about which axis was dropped, rather than
an aborted measurement.

## Multi-session handling

Many real corpora consist of dozens or hundreds of short
conversations rather than one long one. The package already
has a hard floor of **500 timesteps** for `memory`; a single
chat session rarely clears it. Two conventions from the wider
ecosystem govern how to handle this:

- **Reinforcement Learning** (Gymnasium, stable-baselines3):
  episodes are kept as separate sequences; episode boundaries
  are explicit (`done=True` / `truncated=True`) and never
  crossed by an estimator.
- **Time-series in pandas / scikit-learn**:
  `MultiIndex (group_id, t)` plus group-aware splitters
  (`GroupKFold`, `TimeSeriesSplit`) prevent group leakage.

The adapter follows both:

- The constructor accepts either a single transcript or a
  **list of transcripts**. Internally each transcript is
  treated as a separate sequence; the adapter never silently
  concatenates two sessions into one trajectory.
- For axes with hard length floors (`memory` ≥ 500),
  the adapter computes the metric **per session** when at
  least one session clears the floor, and aggregates by
  weighted mean. If no single session clears the floor, the
  axis is reported as `None` (mosaic dropout). The aggregation
  is documented in the result metadata.
- A user who genuinely wants a concatenated corpus can pass
  `concatenate_sessions=True`, which emits an explicit warning
  and inserts a sentinel discontinuity marker. This is opt-in,
  not the default.

This gives the user the same hygiene that
`sklearn.model_selection.GroupKFold` enforces in the rest of
the ecosystem: groups stay groups unless you ask explicitly
for them not to.

## Axes enabled by this adapter

A transcript exposes some channels the protocol cares about
and not others. The exact contract is:

| Axis | Status under `LLMTranscriptAdapter` (off-line) | Reason |
| :--- | :---: | :----- |
| `closure`     | ✓ | Reads `state` / `env` arrays; nothing transcript-specific is missing. |
| `memory`      | ✓ | Same; needs corpus length ≥ 500 (per session, see above). |
| `coherence`   | ✓ | The point of the adapter; reads `(declared, executed)`. |
| `constraint`  | ✗ → reports `None` | A transcript does not expose the LLM's internal causal graph between constraints; there is nothing to populate `get_causal_graph` with. |
| `persistence` | ✗ → reports `None` | Requires re-running the model from a perturbed state, which the off-line adapter cannot do. |

The adapter **does not pretend** to cover the missing two
axes. The orchestrator's mosaic dropout policy makes the gap
visible in the resulting profile, in line with the package's
v0.8.0a0 verdict ("the atlas is a mosaic"). Closing the
`persistence` gap is the single most important reason to
build the on-line counterpart in a later release.

The on-line counterpart, when it ships, will additionally
enable `persistence` (single-token / single-message
perturbations replayed through the live API). It will not
help with `constraint`; that gap is structural and remains a
known property of all transcript-based substrates.

## Validation boundary (instrument vs. study)

The package ships the **instrument**: the adapter, the
metrics, the discretisation utilities, and a reference
schema. It does **not** ship the validation against external
behavioural references, by design.

The validation plan recorded in `docs/RAI.md` (correlation of
`rai_proxy_persistence` against C-RAI and against
goal-directedness scoring on transcripts; correlation of
`coherence` against published CoT-faithfulness scores) is
**deferred to studies external to this repository**, with
their pre-registered thresholds already on record. This
mirrors how `statsmodels`, `scikit-learn` and `PyPhi` separate
estimator code from empirical validation: the package guards
the inference machinery; downstream studies guard the
empirical claims.

The adapter therefore deliberately stops at the point where
a profile is produced. It does not bundle a benchmark of
"what `coherence` looks like on real Claude / GPT
transcripts". That benchmark, when run, lives in a separate
study repository that imports `autonometrics` as a dependency.

## API surface (preview)

The exact signatures are fixed at PR2 implementation time;
the shape below is the contract this document locks in.

```python
from autonometrics.adapters import LLMTranscriptAdapter

# Path A — load JSONL produced by an OpenAI / Anthropic
# logging pipeline.
adapter = LLMTranscriptAdapter.from_jsonl("session_001.jsonl")

# Path B — pass an in-memory message list.
adapter = LLMTranscriptAdapter.from_messages(messages)

# Path C — pass a DataFrame whose columns the adapter
# already knows.
adapter = LLMTranscriptAdapter(
    df,
    state_col="executed",
    env_col="env",
    declared_col="reasoning",
    session_col="session_id",          # optional
    to_state_id=None,                  # optional callable
)

# Once built, it is a regular AutonomySystem.
import autonometrics as anm
profile = anm.measure(adapter)

profile.coherence       # float in [0, 1] when defined; else None
profile.closure         # always defined
profile.memory          # defined iff total length per session ≥ 500
profile.constraint      # None — adapter does not expose causal graph
profile.persistence     # None — adapter is off-line
profile.to_dict()       # canonical dictionary, with None for missing
profile.defined_axes()  # sequence of axes actually computed
```

The factory methods on the adapter are named
`from_jsonl(path)` and `from_messages(messages)` to follow
the package convention established at `v0.8.2a0`
(`PromisedCycle.simple()`, `SimpleAutomaton.demo()`,
`CSVTrajectory.from_file()`) — short verbs, sensible
defaults, the verbose constructor available for power users.

## Test plan (pre-PR2)

The PR2 implementation will ship with at least:

- A synthetic Messages-format fixture in `tests/fixtures/`
  with both `tool_calls` and plain replies, with and without
  a `reasoning` block. ~30 turns, multi-session.
- Unit tests for: round-trip JSONL load, automatic
  `LabelEncoder` discretisation, callable override, mosaic
  dropout when `declared` is empty, multi-session aggregation,
  error path when both `tool_calls` and `content` are missing.
- An end-to-end test that constructs the adapter from the
  fixture, calls `anm.measure(adapter)`, and asserts which
  axes are populated and which are `None`. This test is the
  contract this document is locking in.

## Out of scope for `v0.9.0a0`

These items are deliberately deferred:

- `LLMLiveAdapter` (on-line replay; requires API credentials,
  perturbation policy, cost handling). Targeted for `v0.9.1a0`
  or `v0.10.0a0`.
- A canonical embedding-based discretisation (the default
  tool-call-name encoder is sufficient for v0.9.0a0; embedding
  pipelines belong to downstream studies).
- A built-in benchmark over public transcript corpora. Lives
  in external study repositories per the validation-boundary
  decision above.
- Direct integration with LangSmith / OpenTelemetry GenAI
  exporters. The shared Messages format already covers the
  vast majority of real-world cases; bespoke connectors can
  follow if the demand appears.

## Summary

The adapter is a thin translator. It speaks the canonical
LLM API on one side (Messages format), the canonical
`AutonomySystem` protocol on the other, and follows
established scientific-Python conventions (`LabelEncoder`,
mosaic dropout, group-aware sessions) at every fork. The
contract above is the one PR2 implements; the rest of the
v0.9.0 cycle ships factories, README updates, and the version
bump.
