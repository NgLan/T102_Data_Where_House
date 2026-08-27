"""Đọc raw LangChain response thành text và metadata provider-neutral."""

from src.common.utils.json import safe_json_dumps
from src.infrastructure.llm.structured_output_models import StructuredInvocationMetadata


def extract_raw_text(raw: object) -> str | None:
    """Lấy đúng một JSON candidate từ content hoặc tool arguments."""
    candidates = [*_content_candidates(raw), *_tool_candidates(raw)]
    normalized = tuple(item.strip() for item in candidates if item.strip())
    return normalized[0] if len(normalized) == 1 else None


def extract_metadata(raw: object) -> StructuredInvocationMetadata:
    """Đọc finish/provider/model mà không đưa raw payload vào log."""
    metadata = getattr(raw, "response_metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    finish = metadata.get("finish_reason") or metadata.get("stop_reason")
    provider = metadata.get("model_provider") or metadata.get("provider")
    model = metadata.get("model_name") or metadata.get("model")
    usage = _usage_metadata(raw, metadata)
    return StructuredInvocationMetadata(
        str(finish) if finish is not None else None,
        str(provider) if provider is not None else None,
        str(model) if model is not None else None,
        _integer(usage.get("input_tokens") or usage.get("prompt_tokens")),
        _integer(usage.get("output_tokens") or usage.get("completion_tokens")),
        _integer(usage.get("total_tokens")),
    )


def _usage_metadata(raw: object, response_metadata: dict[str, object]) -> dict[str, object]:
    usage = getattr(raw, "usage_metadata", None)
    if not isinstance(usage, dict):
        usage = response_metadata.get("token_usage") or response_metadata.get("usage")
    return usage if isinstance(usage, dict) else {}


def _integer(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _content_candidates(raw: object) -> list[str]:
    content = getattr(raw, "content", None)
    if isinstance(content, str):
        return [content]
    if not isinstance(content, list):
        return []
    candidates = []
    for block in content:
        if isinstance(block, str):
            candidates.append(block)
        elif isinstance(block, dict):
            value = block.get("text") or block.get("content")
            if isinstance(value, str):
                candidates.append(value)
    return candidates


def _tool_candidates(raw: object) -> list[str]:
    calls = getattr(raw, "tool_calls", None)
    if not isinstance(calls, list):
        return []
    candidates = []
    for call in calls:
        if not isinstance(call, dict):
            continue
        arguments = call.get("args") or call.get("arguments")
        if isinstance(arguments, str):
            candidates.append(arguments)
        elif isinstance(arguments, dict):
            candidates.append(safe_json_dumps(arguments))
    return candidates
