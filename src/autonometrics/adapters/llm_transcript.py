"""Off-line LLM transcript adapter for the v0.9.0 release cycle.

``LLMTranscriptAdapter`` translates a recorded conversation between a
user and a chat-style LLM agent into the :class:`AutonomySystem`
protocol that the rest of the package speaks. It accepts the standard
**OpenAI / Anthropic Messages format** so users with logged API
conversations have zero reformatting work to do.

The adapter is **off-line**: it consumes a finished transcript. It
therefore enables the ``closure``, ``memory`` and ``coherence`` axes,
and reports ``None`` for ``constraint`` (a transcript does not expose
the model's internal causal graph) and ``persistence`` (the off-line
adapter cannot replay the model from a perturbed state). Both gaps
are surfaced through the package's existing mosaic-dropout policy.

Field-to-axis mapping:

- ``executed`` <- the assistant's emitted action: the first
  ``tool_calls[0]`` name when present, else the literal label
  ``"respond_to_user"``.
- ``declared`` <- the assistant's reasoning block (``reasoning``,
  ``thinking``) when present; absent when neither field is supplied.
  Turns without a ``declared`` value are dropped from the
  ``coherence`` computation through the per-turn sentinel
  :data:`SENTINEL_NO_DECLARED` and never zero-padded.
- ``env`` <- the concatenation of every ``user`` / ``tool`` /
  ``system`` content arriving between the previous assistant turn and
  the current one.

Discretisation follows the scientific-Python convention: integer
arrays pass through, string / object iterables are auto-encoded with
a deterministic ``dict``-based label encoder stored on the instance,
and a user-supplied ``to_state_id`` callable bypasses both. See
``docs/LLM_TRANSCRIPT.md`` for the full design contract.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import numpy as np

DEFAULT_RESPOND_LABEL = "respond_to_user"
SENTINEL_NO_DECLARED = -1


class LLMTranscriptAdapter:
    """Wrap an off-line LLM conversation as an :class:`AutonomySystem`.

    Parameters
    ----------
    executed:
        Per-turn executed action. Either an integer array (used as-is)
        or any iterable of hashables (auto-encoded).
    env:
        Per-turn environment summary, same length as ``executed``. Same
        encoding rules apply.
    declared:
        Optional per-turn declared intent. ``None`` (or empty string)
        for a turn signals that the model produced no reasoning at
        that turn; such turns are excluded from ``coherence`` rather
        than zero-padded. When the entire sequence is missing,
        :meth:`get_declared_executed` returns ``None`` so the
        orchestrator records ``coherence`` as missing under mosaic
        dropout.
    to_state_id:
        Optional callable ``Any -> int`` applied to every value across
        all three columns. When provided, the built-in encoder is
        skipped entirely.

    Notes
    -----
    The adapter exposes ``executed_encoder_``, ``env_encoder_`` and
    ``declared_encoder_`` (each a ``dict[Any, int]`` or ``None``) so
    callers can inspect the resulting label mapping. These attributes
    are inspired by the scikit-learn ``*_`` convention for fitted
    state and are read-only by convention.
    """

    def __init__(
        self,
        *,
        executed: Sequence[Any] | np.ndarray,
        env: Sequence[Any] | np.ndarray,
        declared: Sequence[Any] | np.ndarray | None = None,
        to_state_id: Callable[[Any], int] | None = None,
    ) -> None:
        executed_list = list(executed)
        env_list = list(env)

        if len(executed_list) != len(env_list):
            raise ValueError(
                f"executed and env must have the same length: "
                f"{len(executed_list)} vs {len(env_list)}"
            )
        if len(executed_list) < 2:
            raise ValueError(
                f"transcript must contain at least 2 turns; got {len(executed_list)}"
            )

        if declared is not None:
            declared_list: list[Any] | None = list(declared)
            if len(declared_list) != len(executed_list):
                raise ValueError(
                    f"declared must match executed length: "
                    f"{len(declared_list)} vs {len(executed_list)}"
                )
        else:
            declared_list = None

        if to_state_id is not None:
            self._executed = np.asarray(
                [int(to_state_id(x)) for x in executed_list], dtype=np.int64
            )
            self._env = np.asarray(
                [int(to_state_id(x)) for x in env_list], dtype=np.int64
            )
            self.executed_encoder_: dict[Any, int] | None = None
            self.env_encoder_: dict[Any, int] | None = None
            if declared_list is not None:
                self._declared_arr: np.ndarray | None = np.asarray(
                    [
                        SENTINEL_NO_DECLARED if _is_empty(x) else int(to_state_id(x))
                        for x in declared_list
                    ],
                    dtype=np.int64,
                )
                self.declared_encoder_: dict[Any, int] | None = None
            else:
                self._declared_arr = None
                self.declared_encoder_ = None
        else:
            self._executed, self.executed_encoder_ = _encode_or_passthrough(executed_list)
            self._env, self.env_encoder_ = _encode_or_passthrough(env_list)
            if declared_list is not None:
                normalised = [None if _is_empty(x) else x for x in declared_list]
                self._declared_arr, self.declared_encoder_ = _encode_with_sentinel(normalised)
            else:
                self._declared_arr = None
                self.declared_encoder_ = None

        if self._declared_arr is None:
            self._has_declared = False
            self._valid_mask: np.ndarray | None = None
        else:
            self._valid_mask = self._declared_arr != SENTINEL_NO_DECLARED
            self._has_declared = bool(self._valid_mask.any())

    @classmethod
    def from_messages(
        cls,
        messages: list[dict[str, Any]],
        *,
        to_state_id: Callable[[Any], int] | None = None,
    ) -> LLMTranscriptAdapter:
        """Parse an OpenAI / Anthropic Messages list into an adapter.

        ``messages`` is the list-of-dicts shape every major chat-style
        LLM provider already emits. This factory walks the list once,
        accumulates ``user`` / ``tool`` / ``system`` content between
        assistant turns into ``env``, and emits one timestep per
        assistant turn.

        Multi-session corpora (a list-of-lists) are not supported in
        this entry point; pass each session through the factory
        separately and aggregate downstream. Per-session aggregation
        inside the orchestrator is tracked for a follow-up PR; see the
        v0.9.0 contract in ``docs/LLM_TRANSCRIPT.md``.
        """
        if not isinstance(messages, list):
            raise TypeError(
                f"messages must be a list of dicts; got {type(messages).__name__}"
            )
        if messages and isinstance(messages[0], list):
            raise NotImplementedError(
                "multi-session corpora (list-of-lists) are not yet supported "
                "by from_messages; build one adapter per session and aggregate "
                "downstream. Tracked for a follow-up PR; see docs/LLM_TRANSCRIPT.md."
            )

        executed: list[str] = []
        declared: list[str | None] = []
        env: list[str] = []
        env_buffer: list[str] = []

        for msg in messages:
            if not isinstance(msg, dict):
                raise ValueError(
                    f"every message must be a dict; got {type(msg).__name__}"
                )
            role = msg.get("role")
            if role in ("user", "tool", "system"):
                content = msg.get("content")
                if content:
                    env_buffer.append(str(content))
            elif role == "assistant":
                tool_calls = msg.get("tool_calls") or []
                if tool_calls:
                    name = _extract_tool_name(tool_calls[0])
                    executed.append(name or DEFAULT_RESPOND_LABEL)
                else:
                    executed.append(DEFAULT_RESPOND_LABEL)

                reasoning = msg.get("reasoning") or msg.get("thinking")
                if reasoning and str(reasoning).strip():
                    declared.append(str(reasoning))
                else:
                    declared.append(None)

                env.append(" | ".join(env_buffer) if env_buffer else "")
                env_buffer = []
            else:
                continue

        if len(executed) < 2:
            raise ValueError(
                f"transcript must contain at least 2 assistant turns; got {len(executed)}"
            )

        return cls(
            executed=executed,
            env=env,
            declared=declared,
            to_state_id=to_state_id,
        )

    @classmethod
    def from_jsonl(
        cls,
        path: str | Path,
        *,
        to_state_id: Callable[[Any], int] | None = None,
    ) -> LLMTranscriptAdapter:
        """Load a JSONL file (one Messages-format dict per line).

        Empty / whitespace-only lines are silently skipped; everything
        else must be a JSON object. Raises ``FileNotFoundError`` when
        the path does not exist and ``ValueError`` on malformed lines.
        """
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"JSONL transcript not found: {p}")

        messages: list[dict[str, Any]] = []
        with p.open("r", encoding="utf-8") as fh:
            for line_num, raw in enumerate(fh, start=1):
                line = raw.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"invalid JSON at line {line_num} of {p}: {exc.msg}"
                    ) from exc
                if not isinstance(msg, dict):
                    raise ValueError(
                        f"line {line_num} of {p} is not a JSON object: {msg!r}"
                    )
                messages.append(msg)

        if not messages:
            raise ValueError(f"JSONL transcript is empty: {p}")

        return cls.from_messages(messages, to_state_id=to_state_id)

    def get_state_history(self) -> np.ndarray:
        return self._executed.copy()

    def get_env_history(self) -> np.ndarray:
        return self._env.copy()

    def get_declared_executed(self) -> tuple[np.ndarray, np.ndarray] | None:
        """Return the ``(declared, executed)`` pair for the coherence axis.

        Returns ``None`` whenever no usable ``declared`` value is
        available (no reasoning anywhere in the transcript, or fewer
        than two valid pairs after sentinel filtering). The
        orchestrator interprets ``None`` as mosaic dropout for the
        ``coherence`` axis.
        """
        if not self._has_declared or self._declared_arr is None or self._valid_mask is None:
            return None
        declared_valid = self._declared_arr[self._valid_mask]
        executed_valid = self._executed[self._valid_mask]
        if declared_valid.size < 2:
            return None
        return declared_valid, executed_valid


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _is_int_iterable(values: list[Any]) -> bool:
    return all(
        isinstance(v, (int, np.integer)) and not isinstance(v, bool)
        for v in values
    )


def _encode_or_passthrough(values: list[Any]) -> tuple[np.ndarray, dict[Any, int] | None]:
    if _is_int_iterable(values):
        return np.asarray(values, dtype=np.int64), None
    encoder: dict[Any, int] = {}
    out: list[int] = []
    for v in values:
        if v not in encoder:
            encoder[v] = len(encoder)
        out.append(encoder[v])
    return np.asarray(out, dtype=np.int64), encoder


def _encode_with_sentinel(values: list[Any]) -> tuple[np.ndarray, dict[Any, int]]:
    encoder: dict[Any, int] = {}
    out: list[int] = []
    for v in values:
        if v is None:
            out.append(SENTINEL_NO_DECLARED)
        else:
            if v not in encoder:
                encoder[v] = len(encoder)
            out.append(encoder[v])
    return np.asarray(out, dtype=np.int64), encoder


def _extract_tool_name(tool_call: Any) -> str | None:
    """Return the tool / function name from an OpenAI / Anthropic tool_call."""
    if not isinstance(tool_call, dict):
        return None
    fn = tool_call.get("function")
    if isinstance(fn, dict):
        name = fn.get("name")
        if isinstance(name, str) and name:
            return name
    name = tool_call.get("name")
    if isinstance(name, str) and name:
        return name
    return None
