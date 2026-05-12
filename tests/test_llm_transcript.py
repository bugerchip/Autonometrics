"""Tests for the LLMTranscriptAdapter (v0.9.0a0 contract)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest

import autonometrics as anm
from autonometrics.adapters.llm_transcript import (
    DEFAULT_RESPOND_LABEL,
    SENTINEL_NO_DECLARED,
    LLMTranscriptAdapter,
)


def _openai_assistant(
    *,
    content: str | None = None,
    reasoning: str | None = None,
    tool_name: str | None = None,
) -> dict[str, Any]:
    msg: dict[str, Any] = {"role": "assistant"}
    if content is not None:
        msg["content"] = content
    if reasoning is not None:
        msg["reasoning"] = reasoning
    if tool_name is not None:
        msg["tool_calls"] = [
            {"type": "function", "function": {"name": tool_name, "arguments": "{}"}}
        ]
    return msg


def _anthropic_assistant(
    *,
    thinking: str | None = None,
    tool_name: str | None = None,
    content: str | None = None,
) -> dict[str, Any]:
    msg: dict[str, Any] = {"role": "assistant"}
    if content is not None:
        msg["content"] = content
    if thinking is not None:
        msg["thinking"] = thinking
    if tool_name is not None:
        msg["tool_calls"] = [{"type": "tool_use", "name": tool_name, "input": {}}]
    return msg


def _build_basic_messages() -> list[dict[str, Any]]:
    """Six-turn synthetic conversation with reasoning + tool calls.

    Used by smoke tests of the parsing layer (not the metrics layer).
    """
    return [
        {"role": "system", "content": "You are an assistant."},
        {"role": "user", "content": "Read file X then summarize."},
        _openai_assistant(reasoning="I will read file X.", tool_name="read_file"),
        {"role": "tool", "content": "<contents of file X>"},
        _openai_assistant(reasoning="Now I will summarize.", tool_name="respond_to_user"),
        {"role": "user", "content": "Now check Y."},
        _openai_assistant(reasoning="I will read file Y.", tool_name="read_file"),
        {"role": "tool", "content": "<contents of file Y>"},
        _openai_assistant(reasoning="Final answer.", content="Done."),
        {"role": "user", "content": "Thanks."},
        _openai_assistant(reasoning="Acknowledge.", content="You're welcome."),
    ]


def _build_repeating_messages(n_cycles: int = 8) -> list[dict[str, Any]]:
    """Synthetic conversation whose env recurs and whose actions vary.

    The closure axis needs ``H(S_{t+1} | E_t) > 0``: given an env, the
    next state must take more than one value across the corpus.
    Realistic transcripts satisfy this because the same prompt rarely
    produces the exact same action twice. This fixture emits the same
    user prompt every cycle but alternates the tool the assistant
    picks, so the conditional entropy is non-degenerate.
    """
    tool_pool = ["read_file", "search", "respond_to_user"]
    messages: list[dict[str, Any]] = [{"role": "system", "content": "Assistant."}]
    for i in range(n_cycles):
        tool = tool_pool[i % len(tool_pool)]
        messages.extend(
            [
                {"role": "user", "content": "What's next?"},
                _openai_assistant(reasoning="Plan step.", tool_name=tool),
                {"role": "tool", "content": "<result>"},
                _openai_assistant(reasoning="Reply.", content="Done."),
                {"role": "user", "content": "Confirm please."},
                _openai_assistant(reasoning="Confirm step.", content="Confirmed."),
            ]
        )
    return messages


def test_from_messages_extracts_executed_per_assistant_turn() -> None:
    adapter = LLMTranscriptAdapter.from_messages(_build_basic_messages())
    states = adapter.get_state_history()

    assert states.dtype == np.int64
    assert states.size == 5


def test_from_messages_emits_one_env_per_assistant_turn() -> None:
    adapter = LLMTranscriptAdapter.from_messages(_build_basic_messages())
    env = adapter.get_env_history()

    assert env.size == adapter.get_state_history().size


def test_executed_encoder_maps_tool_calls_to_distinct_ids() -> None:
    adapter = LLMTranscriptAdapter.from_messages(_build_basic_messages())
    encoder = adapter.executed_encoder_

    assert encoder is not None
    assert "read_file" in encoder
    assert "respond_to_user" in encoder
    assert encoder["read_file"] != encoder["respond_to_user"]


def test_assistant_without_tool_call_uses_respond_to_user_label() -> None:
    messages = [
        {"role": "user", "content": "Hello."},
        _openai_assistant(reasoning="Greet back.", content="Hi."),
        {"role": "user", "content": "How are you?"},
        _openai_assistant(reasoning="Answer.", content="Good."),
    ]
    adapter = LLMTranscriptAdapter.from_messages(messages)

    assert adapter.executed_encoder_ is not None
    assert DEFAULT_RESPOND_LABEL in adapter.executed_encoder_


def test_anthropic_tool_use_format_is_supported() -> None:
    messages = [
        {"role": "user", "content": "Q1"},
        _anthropic_assistant(thinking="plan A", tool_name="search"),
        {"role": "user", "content": "Q2"},
        _anthropic_assistant(thinking="plan B", tool_name="search"),
    ]
    adapter = LLMTranscriptAdapter.from_messages(messages)

    assert adapter.executed_encoder_ is not None
    assert "search" in adapter.executed_encoder_


def test_thinking_field_populates_declared() -> None:
    messages = [
        {"role": "user", "content": "Q1"},
        _anthropic_assistant(thinking="plan A", tool_name="search"),
        {"role": "user", "content": "Q2"},
        _anthropic_assistant(thinking="plan B", tool_name="search"),
    ]
    adapter = LLMTranscriptAdapter.from_messages(messages)
    pair = adapter.get_declared_executed()

    assert pair is not None
    declared, executed = pair
    assert declared.size == 2
    assert executed.size == 2


def test_get_declared_executed_returns_none_without_reasoning() -> None:
    messages = [
        {"role": "user", "content": "Q1"},
        _openai_assistant(content="A1"),
        {"role": "user", "content": "Q2"},
        _openai_assistant(content="A2"),
    ]
    adapter = LLMTranscriptAdapter.from_messages(messages)

    assert adapter.get_declared_executed() is None


def test_partial_reasoning_filters_through_sentinel() -> None:
    messages = [
        {"role": "user", "content": "Q1"},
        _openai_assistant(reasoning="r1", content="A1"),
        {"role": "user", "content": "Q2"},
        _openai_assistant(content="A2"),
        {"role": "user", "content": "Q3"},
        _openai_assistant(reasoning="r3", content="A3"),
    ]
    adapter = LLMTranscriptAdapter.from_messages(messages)
    pair = adapter.get_declared_executed()

    assert pair is not None
    declared, executed = pair
    assert declared.size == 2
    assert executed.size == 2
    assert SENTINEL_NO_DECLARED not in declared


def test_whitespace_only_reasoning_treated_as_missing() -> None:
    messages = [
        {"role": "user", "content": "Q1"},
        _openai_assistant(reasoning="   ", content="A1"),
        {"role": "user", "content": "Q2"},
        _openai_assistant(reasoning="r2", content="A2"),
    ]
    adapter = LLMTranscriptAdapter.from_messages(messages)
    pair = adapter.get_declared_executed()

    assert pair is None or pair[0].size == 1


def test_constructor_with_pre_encoded_int_arrays_passes_through() -> None:
    adapter = LLMTranscriptAdapter(
        executed=[0, 1, 0, 1, 0],
        env=[2, 2, 3, 3, 2],
        declared=[0, 1, 0, 1, 0],
    )

    np.testing.assert_array_equal(adapter.get_state_history(), [0, 1, 0, 1, 0])
    np.testing.assert_array_equal(adapter.get_env_history(), [2, 2, 3, 3, 2])
    assert adapter.executed_encoder_ is None


def test_constructor_callable_overrides_built_in_encoder() -> None:
    def custom(s: object) -> int:
        return hash(str(s)) % 7

    adapter = LLMTranscriptAdapter(
        executed=["read", "write", "read", "respond"],
        env=["q1", "q2", "q3", "q4"],
        declared=["plan a", "plan b", "plan c", "plan d"],
        to_state_id=custom,
    )

    assert adapter.executed_encoder_ is None
    assert adapter.env_encoder_ is None
    assert adapter.declared_encoder_ is None
    states = adapter.get_state_history()
    assert states.dtype == np.int64
    assert (states < 7).all() and (states >= 0).all()


def test_constructor_rejects_length_mismatch() -> None:
    with pytest.raises(ValueError, match="same length"):
        LLMTranscriptAdapter(
            executed=[0, 1, 0],
            env=[2, 2],
        )


def test_constructor_rejects_too_short() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        LLMTranscriptAdapter(executed=[0], env=[1])


def test_constructor_rejects_declared_length_mismatch() -> None:
    with pytest.raises(ValueError, match="declared must match"):
        LLMTranscriptAdapter(
            executed=[0, 1, 0],
            env=[1, 2, 1],
            declared=[0, 1],
        )


def test_from_messages_rejects_too_few_assistant_turns() -> None:
    messages = [
        {"role": "user", "content": "Q1"},
        _openai_assistant(content="A1"),
    ]
    with pytest.raises(ValueError, match="at least 2 assistant turns"):
        LLMTranscriptAdapter.from_messages(messages)


def test_from_messages_rejects_non_dict_entries() -> None:
    with pytest.raises(ValueError, match="every message must be a dict"):
        LLMTranscriptAdapter.from_messages([{"role": "user", "content": "Q1"}, "not a dict"])  # type: ignore[list-item]


def test_from_messages_rejects_list_of_lists_with_clear_message() -> None:
    sessions = [
        [{"role": "user", "content": "Q"}],
        [{"role": "user", "content": "Q"}],
    ]
    with pytest.raises(NotImplementedError, match="multi-session"):
        LLMTranscriptAdapter.from_messages(sessions)  # type: ignore[arg-type]


def test_from_jsonl_round_trip(tmp_path: Path) -> None:
    messages = _build_basic_messages()
    path = tmp_path / "session.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for msg in messages:
            fh.write(json.dumps(msg) + "\n")

    adapter = LLMTranscriptAdapter.from_jsonl(path)

    direct = LLMTranscriptAdapter.from_messages(messages)
    np.testing.assert_array_equal(adapter.get_state_history(), direct.get_state_history())
    np.testing.assert_array_equal(adapter.get_env_history(), direct.get_env_history())


def test_from_jsonl_skips_blank_lines(tmp_path: Path) -> None:
    path = tmp_path / "session.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for msg in _build_basic_messages():
            fh.write(json.dumps(msg) + "\n\n")

    adapter = LLMTranscriptAdapter.from_jsonl(path)

    assert adapter.get_state_history().size == 5


def test_from_jsonl_raises_on_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="JSONL transcript not found"):
        LLMTranscriptAdapter.from_jsonl(tmp_path / "missing.jsonl")


def test_from_jsonl_raises_on_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "broken.jsonl"
    path.write_text('{"role": "user"\n', encoding="utf-8")

    with pytest.raises(ValueError, match="invalid JSON at line 1"):
        LLMTranscriptAdapter.from_jsonl(path)


def test_from_jsonl_raises_on_non_object_line(tmp_path: Path) -> None:
    path = tmp_path / "list.jsonl"
    path.write_text('["not", "a", "dict"]\n', encoding="utf-8")

    with pytest.raises(ValueError, match="not a JSON object"):
        LLMTranscriptAdapter.from_jsonl(path)


def test_from_jsonl_raises_on_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.jsonl"
    path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="JSONL transcript is empty"):
        LLMTranscriptAdapter.from_jsonl(path)


def test_adapter_does_not_expose_causal_graph() -> None:
    adapter = LLMTranscriptAdapter.from_messages(_build_basic_messages())
    assert not hasattr(adapter, "get_causal_graph")


def test_adapter_does_not_expose_replay_from_perturbation() -> None:
    adapter = LLMTranscriptAdapter.from_messages(_build_basic_messages())
    assert not hasattr(adapter, "replay_from_perturbation")


def test_end_to_end_measure_reports_expected_axes_off_line() -> None:
    """Contract assertion: closure / coherence defined, constraint /
    persistence reported as None under mosaic dropout."""
    messages = _build_repeating_messages(n_cycles=6)
    adapter = LLMTranscriptAdapter.from_messages(messages)

    profile = anm.measure(
        adapter,
        axes=["closure", "constraint", "persistence", "coherence"],
    )

    assert profile.closure is not None
    assert profile.constraint is None
    assert profile.persistence is None
    assert profile.coherence is not None


def test_end_to_end_memory_raises_below_hard_floor() -> None:
    """Memory needs >=500 timesteps; below the floor the estimator
    refuses to run, by package-wide policy. This is *not* mosaic
    dropout: length precondition is on the user, not on the adapter."""
    messages = _build_repeating_messages(n_cycles=6)
    adapter = LLMTranscriptAdapter.from_messages(messages)

    with pytest.raises(ValueError, match="too short"):
        anm.measure(adapter, axes=["memory"])


def test_end_to_end_coherence_none_when_no_reasoning_anywhere() -> None:
    messages = [{"role": "system", "content": "Assistant."}]
    for _ in range(6):
        messages.extend(
            [
                {"role": "user", "content": "What's next?"},
                _openai_assistant(content="Here you go."),
                {"role": "user", "content": "Confirm please."},
                _openai_assistant(content="Confirmed."),
            ]
        )
    adapter = LLMTranscriptAdapter.from_messages(messages)

    profile = anm.measure(adapter, axes=["coherence"])
    assert profile.coherence is None


def test_top_level_export_available() -> None:
    assert hasattr(anm, "LLMTranscriptAdapter")
    assert anm.LLMTranscriptAdapter is LLMTranscriptAdapter
