from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from services.request_detail_view import request_proxy_source_label, request_status_presentation


MONITOR_SCHEMA_VERSION = 1

ENTRY_QUEUE_METRIC_KEYS = ("handler_queue_ms", "stream_first_queue_ms")

DIGEST_METRIC_PAIRS = (
    ('Waiting for ingress', "handler_queue_ms"),
    ('First response', "stream_first_queue_ms"),
    ('Waiting for account', "account_wait_ms"),
    ('Waiting for egress', "egress_wait_ms"),
    ('Egress lease', "egress_acquire_ms"),
    ('Upload', "upload_ms"),
    ('Initialize', "bootstrap_ms"),
    ('Token', "requirements_ms"),
    ('Prepare', "prepare_conversation_ms"),
    ('Start', "generation_start_ms"),
    ('HTTP first response', "http_ttfb_ms"),
    ('HTTP wait', "http_wait_ms"),
    ('SSE first event', "sse_first_event_ms"),
    ('SSE gap', "sse_max_gap_ms"),
    ('Upstream generation', "conversation_stream_ms"),
    ('Upstream disconnect', "stream_error_ms"),
    ('Wait for result', "poll_wait_ms"),
    ('Query result', "poll_request_ms"),
    ('Process result', "resolve_ms"),
    ('Download', "download_ms"),
)

SLOW_METRIC_PAIRS = (
    ("handler_queue_ms", 'Waiting for ingress'),
    ("stream_first_queue_ms", 'First response'),
    ("account_wait_ms", 'Waiting for account'),
    ("egress_wait_ms", 'Waiting for egress'),
    ("egress_acquire_ms", 'Egress lease'),
    ("upload_ms", 'Upload'),
    ("bootstrap_ms", 'Initialize'),
    ("requirements_ms", 'Token'),
    ("prepare_conversation_ms", 'Prepare'),
    ("generation_start_ms", 'Start'),
    ("http_dns_ms", "HTTP DNS"),
    ("http_tcp_ms", "HTTP TCP"),
    ("http_tls_ms", "HTTP TLS"),
    ("http_wait_ms", 'HTTP wait'),
    ("http_ttfb_ms", 'HTTP first response'),
    ("sse_first_event_ms", 'SSE first event'),
    ("sse_max_gap_ms", 'Maximum SSE gap'),
    ("sse_last_gap_ms", 'SSE closing gap'),
    ("conversation_stream_ms", 'Upstream generation'),
    ("stream_error_ms", 'Upstream disconnect'),
    ("poll_wait_ms", 'Wait for result'),
    ("poll_request_ms", 'Query result'),
    ("resolve_ms", 'Process result'),
    ("download_ms", 'Download'),
    ("response_ms", 'Format response'),
)

EVENT_METRIC_PAIRS = (
    ('Waiting for ingress', "handler_queue_ms"),
    ('First response', "stream_first_queue_ms"),
    ('Waiting for account', "account_wait_ms"),
    ('Waiting for egress', "egress_wait_ms"),
    ('Upload', "upload_ms"),
    ('Initialize', "bootstrap_ms"),
    ('Token', "requirements_ms"),
    ('Prepare', "prepare_conversation_ms"),
    ('Start', "generation_start_ms"),
    ('HTTP first response', "http_ttfb_ms"),
    ('HTTP wait', "http_wait_ms"),
    ('SSE first event', "sse_first_event_ms"),
    ('SSE gap', "sse_max_gap_ms"),
    ('Upstream generation', "conversation_stream_ms"),
    ('Upstream disconnect', "stream_error_ms"),
    ('Wait for result', "poll_wait_ms"),
    ('Query result', "poll_request_ms"),
    ('Process result', "resolve_ms"),
    ('Download', "download_ms"),
    ('Format response', "response_ms"),
)

LINEAR_STAGE_KEYS = (
    "account_wait_ms",
    "egress_wait_ms",
    "upload_ms",
    "bootstrap_ms",
    "requirements_ms",
    "prepare_conversation_ms",
    "generation_start_ms",
    "conversation_stream_ms",
    "stream_error_ms",
    "poll_wait_ms",
    "poll_request_ms",
    "resolve_ms",
    "download_ms",
    "response_ms",
)

RECORD_FIELDS = {
    "call_id",
    "endpoint",
    "model",
    "summary",
    "role",
    "key_name",
    "status",
    "outcome",
    "stage",
    "stage_label",
    "started_at",
    "ended_at",
    "updated_at",
    "elapsed_ms",
    "stage_elapsed_ms",
    "duration_ms",
    "account_email",
    "previous_account_email",
    "image_account_attempt",
    "image_account_max_attempts",
    "image_account_switch_count",
    "attempt_count",
    "switch_count",
    "image_requested_count",
    "image_succeeded_count",
    "image_failed_count",
    "image_result_status",
    "recovered_after_switch",
    "public_error",
    "conversation_id",
    "error",
    "raw_error",
    "upstream_error",
    "upstream_message",
    "url_count",
    "proxy_source",
    "proxy_hash",
    "egress_key",
    "egress_label",
    "proxy_group_id",
    "proxy_node_id",
    "proxy_node_name",
    "image_egress_limit",
    "has_proxy",
    "egress_mode",
    "local_reason",
    "failure_code",
    "failure_scope",
    "failure_capability",
    "failure_retryable",
    "failure_account_failure",
    "failure_retry_after",
    "status_code",
    "error_type",
    "account_failure",
    "switched_account",
}

IMAGE_FIELDS = {
    "index",
    "total",
    "account_email",
    "previous_account_email",
    "account_attempt",
    "max_account_attempts",
    "account_switch_count",
    "stage",
    "stage_label",
    "updated_at",
    "status",
    "returned_result",
    "returned_message",
    "proxy_source",
    "proxy_hash",
    "egress_key",
    "egress_label",
    "proxy_group_id",
    "proxy_node_id",
    "proxy_node_name",
    "image_egress_limit",
    "has_proxy",
    "egress_mode",
    "local_reason",
    "failure_code",
    "failure_scope",
    "failure_capability",
    "failure_retryable",
    "failure_account_failure",
    "failure_retry_after",
    "status_code",
    "error_type",
    "public_error",
    "account_failure",
    "switched_account",
    "error",
    "raw_error",
    "upstream_error",
    "upstream_message",
}

EVENT_FIELDS = {
    "time",
    "call_id",
    "event",
    "label",
    "model",
    "index",
    "total",
    "attempt",
    "account_email",
    "previous_account_email",
    "account_switch_count",
    "max_account_attempts",
    "status",
    "sse_event_count",
    "proxy_source",
    "proxy_hash",
    "egress_key",
    "egress_label",
    "proxy_group_id",
    "proxy_node_id",
    "proxy_node_name",
    "image_egress_limit",
    "egress_mode",
    "has_proxy",
    "local_reason",
    "failure_code",
    "failure_scope",
    "failure_capability",
    "failure_retryable",
    "failure_account_failure",
    "failure_retry_after",
    "status_code",
    "error_type",
    "public_error",
    "account_failure",
    "switched_account",
    "error",
    "raw_error",
    "upstream_error",
    "upstream_message",
    *(key for _, key in EVENT_METRIC_PAIRS),
    "http_dns_ms",
    "http_tcp_ms",
    "http_tls_ms",
    "http_total_ms",
    "sse_last_gap_ms",
    "sse_stream_ms",
    "stream_ms",
    "total_ms",
}

INTEGER_FIELDS = {
    "elapsed_ms",
    "stage_elapsed_ms",
    "duration_ms",
    "image_account_attempt",
    "image_account_max_attempts",
    "image_account_switch_count",
    "attempt_count",
    "switch_count",
    "image_requested_count",
    "image_succeeded_count",
    "image_failed_count",
    "url_count",
    "image_egress_limit",
    "failure_retry_after",
    "status_code",
    "index",
    "total",
    "account_attempt",
    "max_account_attempts",
    "account_switch_count",
    "attempt",
    "sse_event_count",
}

BOOLEAN_FIELDS = {
    "recovered_after_switch",
    "has_proxy",
    "failure_retryable",
    "failure_account_failure",
    "account_failure",
    "switched_account",
    "returned_result",
    "returned_message",
}


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _int(value: object) -> int:
    try:
        return max(0, int(float(value)))
    except (TypeError, ValueError):
        return 0


def _float(value: object) -> float:
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return 0.0


def _text(value: object) -> str:
    return str(value or "").strip()


def _format_ms(value: object) -> str:
    ms = _int(value)
    if ms <= 0:
        return "-"
    if ms >= 60_000:
        return f"{ms / 60_000:.1f}m"
    if ms >= 1_000:
        return f"{ms / 1_000:.1f}s"
    return f"{ms}ms"


def _metric_map(value: object) -> dict[str, int]:
    return {
        str(key): _int(metric)
        for key, metric in _mapping(value).items()
        if str(key).endswith("_ms")
    }


def _canonical_timings(record: Mapping[str, Any]) -> dict[str, int]:
    metrics = _metric_map(record.get("metrics"))
    perf = _metric_map(record.get("perf"))
    return {
        key: max(metrics.get(key, 0), perf.get(key, 0))
        for key in sorted(metrics.keys() | perf.keys())
    }


def _copy_fields(source: Mapping[str, Any], fields: set[str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in fields:
        if key not in source or source[key] is None:
            continue
        value = source[key]
        if key in INTEGER_FIELDS:
            result[key] = _int(value)
        elif key in BOOLEAN_FIELDS:
            result[key] = bool(value)
        else:
            result[key] = str(value)
    return result


def _build_egress(record: Mapping[str, Any]) -> dict[str, Any]:
    source = str(record.get("proxy_source") or "direct").strip() or "direct"
    source_label = request_proxy_source_label(source)
    group_id = str(record.get("proxy_group_id") or "").strip()
    node_name = str(record.get("proxy_node_name") or "").strip()
    node_id = str(record.get("proxy_node_id") or "").strip()
    node_label = "/".join(value for value in (group_id, node_name or node_id) if value)
    raw_label = str(record.get("egress_label") or "").strip()
    label = node_label
    if not label and raw_label not in {"", "direct", source, f"{source}_profile"} and not raw_label.startswith("proxy:"):
        label = raw_label
    proxy_hash = str(record.get("proxy_hash") or "").strip()
    display = f"{source_label} {label}" if label else source_label
    if not label and proxy_hash and proxy_hash != "direct":
        display = f"{source_label} {proxy_hash}"
    return {
        "source": source,
        "source_label": source_label,
        "label": label,
        "hash": proxy_hash,
        "display": display,
        "key": str(record.get("egress_key") or ""),
        "mode": str(record.get("egress_mode") or ""),
        "group_id": group_id,
        "node_id": node_id,
        "node_name": node_name,
        "has_proxy": bool(record.get("has_proxy")) if "has_proxy" in record else None,
    }


def _build_account_attempt(record: Mapping[str, Any]) -> dict[str, Any]:
    attempt = _int(record.get("image_account_attempt"))
    max_attempts = max(attempt, _int(record.get("image_account_max_attempts")))
    switch_count = _int(record.get("image_account_switch_count"))
    images = _mapping(record.get("images"))
    image_count = max((_int(_mapping(item).get("total")) for item in images.values()), default=0)
    parts: list[str] = []
    if attempt and max_attempts:
        prefix = 'Highest phase #' if image_count > 1 else 'Phase #'
        parts.append(f"{prefix}{attempt}/{max_attempts} times")
    if attempt or max_attempts or switch_count:
        parts.append(f"Switched {switch_count} times" if switch_count else 'Not switched')
    return {
        "attempt": attempt,
        "max_attempts": max_attempts,
        "switch_count": switch_count,
        "image_count": image_count,
        "display": " · ".join(parts),
    }


def _row_duration(record: Mapping[str, Any]) -> int:
    return max(_int(record.get("duration_ms")), _int(record.get("elapsed_ms")))


def _tracked_duration(timings: Mapping[str, int]) -> int:
    queue = sum(_int(timings.get(key)) for key in ENTRY_QUEUE_METRIC_KEYS)
    linear = sum(_int(timings.get(key)) for key in LINEAR_STAGE_KEYS)
    wrapped = max(_int(timings.get("total_ms")), _int(timings.get("stream_ms")), linear)
    return queue + wrapped


def _slow_metrics(record: Mapping[str, Any], timings: Mapping[str, int]) -> tuple[list[dict[str, Any]], int, int]:
    duration = _row_duration(record)
    tracked = _tracked_duration(timings)
    untracked = max(0, duration - tracked)
    items = [
        {
            "key": key,
            "label": label,
            "value_ms": value,
            "value_text": _format_ms(value),
            "important": value >= 10_000,
        }
        for key, label in SLOW_METRIC_PAIRS
        if (value := _int(timings.get(key))) > 0
    ]
    if untracked >= 1_000:
        items.append(
            {
                "key": "untracked_ms",
                "label": 'Unlabeled',
                "value_ms": untracked,
                "value_text": _format_ms(untracked),
                "important": untracked >= 10_000,
            }
        )
    if not items and duration > 0:
        items.append(
            {
                "key": "duration_ms",
                "label": 'Total duration',
                "value_ms": duration,
                "value_text": _format_ms(duration),
                "important": duration >= 10_000,
            }
        )
    return items, tracked, untracked


def _slow_reason(items: list[dict[str, Any]]) -> tuple[str, str]:
    candidates = sorted(
        (item for item in items if item["key"] not in {"stream_ms", "total_ms", "duration_ms"}),
        key=lambda item: item["value_ms"],
        reverse=True,
    )
    if not candidates or candidates[0]["value_ms"] < 1_000:
        return "", ""
    top = candidates[0]
    key = str(top["key"])
    label = str(top["label"])
    value = str(top["value_text"])
    if key == "untracked_ms":
        return "instrumentation_gap", f"Still {value} has no recorded phase; this part of the request has no instrumentation yet."
    if key == "poll_wait_ms":
        return "image_poll_wait", 'The main delay is waiting for an image result. The ChatGPT image task may still be running or polling may be backing off.'
    if key == "poll_request_ms":
        return "image_poll_request", 'The main delay is querying the image result. The task or session endpoint may be slow.'
    if key == "resolve_ms":
        return "image_result_resolve", 'The main delay is processing the result. Converting the image file ID to a download URL may be slow.'
    if key == "conversation_stream_ms":
        return "upstream_generation", 'The main delay is upstream generation. ChatGPT may still be generating the image.'
    if key == "stream_error_ms":
        return "upstream_stream_error", 'The main delay is an upstream disconnect, often caused by HTTP/2 or SSE, the proxy, or an upstream edge node.'
    if key in {"http_ttfb_ms", "http_wait_ms"}:
        return "http_first_byte", 'The main delay is waiting for the first HTTP response, often due to the egress proxy, an upstream edge node, or request queueing.'
    if key in {"http_dns_ms", "http_tcp_ms", "http_tls_ms"}:
        return "http_connect", f"The main delay is in the HTTP connection setup phase: {label} {value}。"
    if key == "sse_first_event_ms":
        return "sse_first_event", 'The main delay is waiting for the first SSE event. The connection is established, but the upstream has not sent an event.'
    if key in {"sse_max_gap_ms", "sse_last_gap_ms"}:
        return "sse_gap", 'The main delay is an SSE gap. The upstream stream paused for a long time between events.'
    if key == "egress_wait_ms":
        return "egress_wait", 'The main delay is waiting for egress. The proxy group, default route, resource proxy, or outbound session setup may be slow.'
    if key in {"upload_ms", "bootstrap_ms", "requirements_ms", "prepare_conversation_ms", "generation_start_ms"}:
        return "upstream_prepare", f"The main delay is in the upstream preparation phase: {label} {value}。"
    if key == "account_wait_ms":
        return "account_wait", 'The main delay is waiting for an account. There may not be enough available accounts, or all account slots may be occupied.'
    if key in set(ENTRY_QUEUE_METRIC_KEYS):
        return "entry_queue", 'The main delay is waiting for ingress. Backend sync thread capacity may be too low. Adjust CHATGPT2API_THREAD_TOKENS to change it.'
    return "primary_metric", f"Main duration: {label} {value}。"


def _status_presentation(record: Mapping[str, Any]) -> tuple[str, str]:
    value = str(record.get("outcome") or record.get("status") or "").lower()
    presentation = request_status_presentation(value, fallback=value or "-")
    return presentation["label"], presentation["tone"]


def _metric_digest(record: Mapping[str, Any], timings: Mapping[str, int]) -> str:
    parts = sorted(
        (
            (value, f"{label} {_format_ms(value)}")
            for label, key in DIGEST_METRIC_PAIRS
            if (value := _int(timings.get(key))) > 0
        ),
        key=lambda item: item[0],
        reverse=True,
    )
    texts = [text for _, text in parts]
    if str(record.get("status") or "").lower() == "running" and _int(record.get("stage_elapsed_ms")) > 0:
        texts.insert(0, f"Current phase {_format_ms(record.get('stage_elapsed_ms'))}")
    return " / ".join(texts[:4]) or "-"


def _project_image(value: object) -> dict[str, Any]:
    image = _mapping(value)
    result = _copy_fields(image, IMAGE_FIELDS)
    result["metrics"] = _metric_map(image.get("metrics"))
    return result


def _project_event(value: object) -> dict[str, Any]:
    event = _mapping(value)
    result = _copy_fields(event, EVENT_FIELDS)
    result.setdefault("time", "")
    result.setdefault("call_id", "")
    result.setdefault("event", "")
    result["label"] = _text(result.get("label")) or _text(result.get("event"))
    parts = [
        f"{label} {_format_ms(event.get(key))}"
        for label, key in EVENT_METRIC_PAIRS
        if _int(event.get(key)) > 0
    ]
    result["timing_text"] = " / ".join(parts[:3]) or "-"
    account_email = _text(event.get("account_email"))
    previous_account_email = _text(event.get("previous_account_email"))
    account_text = (
        f"{previous_account_email} → {account_email}"
        if previous_account_email and account_email
        else account_email
    )
    result["detail_text"] = " · ".join(
        part
        for part in (
            'Switched account' if bool(event.get("switched_account")) else "",
            account_text,
            _text(event.get("public_error")) or _text(event.get("error")),
        )
        if part
    )
    return result


def _project_record(value: object, *, include_detail: bool = False) -> dict[str, Any]:
    record = _mapping(value)
    result = _copy_fields(record, RECORD_FIELDS)
    result.setdefault("call_id", "")
    metrics = _metric_map(record.get("metrics"))
    perf = _metric_map(record.get("perf"))
    timings = _canonical_timings(record)
    result["metrics"] = metrics
    result["perf"] = perf
    result["timings_ms"] = timings
    result["images"] = {
        str(key): _project_image(image)
        for key, image in _mapping(record.get("images")).items()
        if isinstance(image, Mapping)
    }
    egress = _build_egress(record)
    account_attempt = _build_account_attempt(record)
    slow_metrics, tracked, untracked = _slow_metrics(record, timings)
    reason_code, reason = _slow_reason(slow_metrics)
    status_label, status_tone = _status_presentation(record)
    stage_text = _text(record.get("stage_label")) or _text(record.get("stage"))
    if not stage_text:
        stage_text = 'Running' if _text(record.get("status")).lower() == "running" else status_label
    result["egress"] = egress
    result["account_attempt"] = account_attempt
    result["presentation"] = {
        "status_label": status_label,
        "status_tone": status_tone,
        "stage_text": stage_text,
        "error_text": _text(record.get("public_error")) or _text(record.get("error")),
        "duration_text": _format_ms(_row_duration(record)),
        "metric_digest": _metric_digest(record, timings),
        "egress_text": egress["display"],
        "account_attempt_text": account_attempt["display"],
        "account_egress_text": (
            f"Account {_format_ms(timings.get('account_wait_ms'))} / egress {_format_ms(timings.get('egress_wait_ms'))}"
        ),
        "tracked_duration_ms": tracked,
        "untracked_duration_ms": untracked,
        "slow_metrics": slow_metrics,
        "slow_reason_code": reason_code,
        "slow_reason": reason,
    }
    if include_detail:
        raw_events = record.get("events") if isinstance(record.get("events"), list) else []
        result["events"] = [_project_event(event) for event in raw_events]
    return result


def _count_map(value: object) -> dict[str, int]:
    return {str(key): _int(count) for key, count in _mapping(value).items()}


def _project_summary(value: object) -> dict[str, Any]:
    summary = _mapping(value)
    success = _int(summary.get("success"))
    failed = _int(summary.get("failed"))
    rate_limited = _int(summary.get("rate_limited"))
    measured = success + failed + rate_limited
    switch_requests = _int(summary.get("account_switch_requests"))
    switches = _int(summary.get("account_switches"))
    switch_success = _int(summary.get("account_switch_success"))
    metric_p95 = _metric_map(summary.get("metric_p95"))
    active_by_egress = _count_map(summary.get("active_by_egress"))
    slow = _mapping(summary.get("slow_counts"))
    success_rate = _float(summary.get("success_rate"))
    if "success_rate" not in summary:
        success_rate = round(success * 100 / measured, 1) if measured else 0.0
    recovery_rate = _float(summary.get("account_switch_recovery_rate"))
    if "account_switch_recovery_rate" not in summary:
        recovery_rate = round(switch_success * 100 / switch_requests, 1) if switch_requests else 0.0
    return {
        "active": _int(summary.get("active")),
        "completed": _int(summary.get("completed")),
        "success": success,
        "partial_success": _int(summary.get("partial_success")),
        "failed": failed,
        "rate_limited": rate_limited,
        "text_review": _int(summary.get("text_review")),
        "measured": measured,
        "success_rate": success_rate,
        "account_switch_requests": switch_requests,
        "account_switches": switches,
        "account_switch_success": switch_success,
        "account_switch_recovery_rate": recovery_rate,
        "switch_unrecovered": max(0, switch_requests - switch_success),
        "switch_average": round(switches / switch_requests, 1) if switch_requests else 0.0,
        "stream_error_requests": _int(summary.get("stream_error_requests")),
        "avg_duration_ms": _int(summary.get("avg_duration_ms")),
        "p95_duration_ms": _int(summary.get("p95_duration_ms")),
        "entry_queue_p95_ms": max((_int(metric_p95.get(key)) for key in ENTRY_QUEUE_METRIC_KEYS), default=0),
        "active_egress_count": len(active_by_egress),
        "metric_p95": metric_p95,
        "slow_counts": {
            "handler_queue": _int(slow.get("handler_queue")),
            "stream_first_queue": _int(slow.get("stream_first_queue")),
            "account_wait": _int(slow.get("account_wait")),
            "egress_wait": _int(slow.get("egress_wait")),
            "total_over_120s": _int(slow.get("total_over_120s")),
            "local_reject_or_busy": _int(slow.get("local_reject_or_busy")),
        },
        "by_model": _count_map(summary.get("by_model")),
        "active_by_model": _count_map(summary.get("active_by_model")),
        "active_by_egress": active_by_egress,
        "active_by_stage": _count_map(summary.get("active_by_stage")),
    }


def _active_egress_meta(summary: Mapping[str, Any]) -> str:
    items = list(_mapping(summary.get("active_by_egress")).items())
    if not items:
        return 'No active egress routes'
    parts = []
    for key, count in items[:2]:
        source, separator, detail = str(key).partition(":")
        label = request_proxy_source_label(source)
        parts.append(f"{label}{f' {detail}' if separator else ''} {_int(count)}")
    return " / ".join(parts)


def _diagnostic_item(key: str, label: str, value: int | float | str, meta: str, tone: str = "muted") -> dict[str, Any]:
    return {"key": key, "label": label, "value": value, "meta": meta, "tone": tone}


def _build_diagnostic_groups(
    summary: Mapping[str, Any],
    thread_tokens: int,
    completed_window_text: str,
) -> list[dict[str, Any]]:
    p95 = _mapping(summary.get("metric_p95"))
    slow = _mapping(summary.get("slow_counts"))
    local_busy = _int(slow.get("local_reject_or_busy"))
    switch_requests = _int(summary.get("account_switch_requests"))
    switch_count = _int(summary.get("account_switches"))
    switch_success = _int(summary.get("account_switch_success"))
    switch_unrecovered = _int(summary.get("switch_unrecovered"))
    active_egress_meta = _active_egress_meta(summary)
    return [
        {
            "key": "overview",
            "title": 'Live overview',
            "meta": 'Window and results',
            "items": [
                _diagnostic_item("active", 'Current concurrency', _int(summary.get("active")), f"Thread capacity {thread_tokens}"),
                _diagnostic_item("completed", 'Completed window', _int(summary.get("completed")), completed_window_text),
                _diagnostic_item("success", 'Successes', _int(summary.get("success")), 'Succeeded in window', "success"),
                _diagnostic_item("failed", 'Failures', _int(summary.get("failed")), 'Failed in window', "danger" if _int(summary.get("failed")) else "muted"),
                _diagnostic_item("text_review", 'Text responses', _int(summary.get("text_review")), 'Text responses are not counted as failures', "warning"),
                _diagnostic_item("success_rate", 'Success rate', f"{summary.get('success_rate', 0)}%", 'Excludes text responses', "success"),
                _diagnostic_item("slow_total", 'Slow requests', _int(slow.get("total_over_120s")), 'Total duration over 120 seconds', "warning" if _int(slow.get("total_over_120s")) else "muted"),
                _diagnostic_item("rate_limited", 'Rate limits', _int(summary.get("rate_limited")), 'Rate limited in window', "warning"),
            ],
        },
        {
            "key": "entry_egress",
            "title": 'Ingress and egress',
            "meta": 'Local threads, request ingress, proxy egress',
            "items": [
                _diagnostic_item("thread_capacity", 'Thread capacity', thread_tokens, 'Maximum concurrent ingress executions'),
                _diagnostic_item("handler_queue_ms", 'Ingress queue P95', _format_ms(p95.get("handler_queue_ms")), f"Thread capacity {thread_tokens} · slow {_int(slow.get('handler_queue'))}", "info"),
                _diagnostic_item("stream_first_queue_ms", 'First-response queue P95', _format_ms(p95.get("stream_first_queue_ms")), f"Slow {_int(slow.get('stream_first_queue'))}", "info"),
                _diagnostic_item("egress_wait_ms", 'Egress wait P95', _format_ms(p95.get("egress_wait_ms")), active_egress_meta, "info"),
                _diagnostic_item("egress_acquire_ms", 'Egress lease P95', _format_ms(p95.get("egress_acquire_ms")), 'Acquire image egress', "info"),
                _diagnostic_item("active_egress", 'Active egress routes', _int(summary.get("active_egress_count")), active_egress_meta, "info"),
                _diagnostic_item("egress_wait_slow", 'Slow requests waiting for egress', _int(slow.get("egress_wait")), 'Wait longer than 1 second', "warning" if _int(slow.get("egress_wait")) else "muted"),
                _diagnostic_item("local_busy", 'Locally rejected / overloaded', local_busy, 'No account / concurrency / policy', "danger" if local_busy else "muted"),
            ],
        },
        {
            "key": "account_switch",
            "title": 'Accounts and switching',
            "meta": 'Account wait, switching, recovery results',
            "items": [
                _diagnostic_item("account_wait_ms", 'Account wait P95', _format_ms(p95.get("account_wait_ms")), 'Account pool selection', "info"),
                _diagnostic_item("account_wait_slow", 'Slow requests waiting for an account', _int(slow.get("account_wait")), 'Wait longer than 5 seconds', "warning" if _int(slow.get("account_wait")) else "muted"),
                _diagnostic_item("account_switch_requests", 'Requests that switched accounts', switch_requests, 'Requests with an account switch', "warning" if switch_requests else "muted"),
                _diagnostic_item("account_switches", 'Account switches', switch_count, 'Actual switches in window', "warning" if switch_count else "muted"),
                _diagnostic_item("account_switch_success", 'Succeeded after switching accounts', switch_success, 'Recovered request' if switch_requests else 'No account-switch requests', "success" if switch_success else "muted"),
                _diagnostic_item("account_switch_recovery_rate", 'Recovery rate after account switch', f"{summary.get('account_switch_recovery_rate', 0)}%", 'Successful switched requests / requests that switched accounts', "success" if switch_success else "muted"),
                _diagnostic_item("account_switch_unrecovered", 'Account switch did not recover the request', switch_unrecovered, 'Request still failed after switching accounts', "danger" if switch_unrecovered else "muted"),
                _diagnostic_item("account_switch_average", 'Average switches', summary.get("switch_average", 0), 'Per account-switch request', "warning" if switch_count else "muted"),
            ],
        },
        {
            "key": "upstream_prepare",
            "title": 'Upstream preparation',
            "meta": 'Uploads, tokens, sessions, connections',
            "items": [
                _diagnostic_item("upload_ms", 'Image upload', _format_ms(p95.get("upload_ms")), 'Reference image upload'),
                _diagnostic_item("bootstrap_ms", 'Upstream initialization', _format_ms(p95.get("bootstrap_ms")), 'ChatGPT session'),
                _diagnostic_item("requirements_ms", 'Get token', _format_ms(p95.get("requirements_ms")), "requirements / token"),
                _diagnostic_item("prepare_conversation_ms", 'Prepare session', _format_ms(p95.get("prepare_conversation_ms")), 'Prepare image session'),
                _diagnostic_item("generation_start_ms", 'Start generation', _format_ms(p95.get("generation_start_ms")), 'Submit upstream request'),
                _diagnostic_item("http_dns_ms", 'DNS lookup', _format_ms(p95.get("http_dns_ms")), "HTTP DNS P95", "info"),
                _diagnostic_item("http_tcp_ms", 'TCP connection', _format_ms(p95.get("http_tcp_ms")), "HTTP TCP P95", "info"),
                _diagnostic_item("http_tls_ms", 'TLS handshake', _format_ms(p95.get("http_tls_ms")), "HTTP TLS P95", "info"),
            ],
        },
        {
            "key": "generation_transport",
            "title": 'Generation and transport',
            "meta": 'HTTP, SSE, upstream generation, disconnects',
            "items": [
                _diagnostic_item("http_wait_ms", 'HTTP wait', _format_ms(p95.get("http_wait_ms")), 'Request sent to first response', "info"),
                _diagnostic_item("http_ttfb_ms", 'HTTP first response', _format_ms(p95.get("http_ttfb_ms")), 'Request started to first response', "info"),
                _diagnostic_item("sse_first_event_ms", 'SSE first event', _format_ms(p95.get("sse_first_event_ms")), 'Time from connection to first event', "info"),
                _diagnostic_item("sse_max_gap_ms", 'Maximum SSE gap', _format_ms(p95.get("sse_max_gap_ms")), 'Maximum gap between events', "info"),
                _diagnostic_item("sse_last_gap_ms", 'SSE closing gap', _format_ms(p95.get("sse_last_gap_ms")), 'Time from last event to close', "info"),
                _diagnostic_item("conversation_stream_ms", 'Upstream generation', _format_ms(p95.get("conversation_stream_ms")), 'Session stream response', "success"),
                _diagnostic_item("stream_error_requests", 'Requests disconnected', _int(summary.get("stream_error_requests")), 'Disconnected in window', "danger" if _int(summary.get("stream_error_requests")) else "muted"),
                _diagnostic_item("stream_error_ms", 'Disconnect duration P95', _format_ms(p95.get("stream_error_ms")), "HTTP2 / SSE"),
            ],
        },
        {
            "key": "result_delivery",
            "title": 'Results and delivery',
            "meta": 'Total duration, polling, parsing, downloads',
            "items": [
                _diagnostic_item("average", 'Average total duration', _format_ms(summary.get("avg_duration_ms")), 'Window average', "info"),
                _diagnostic_item("p95", 'Total duration P95', _format_ms(summary.get("p95_duration_ms")), 'Slow request reference', "info"),
                _diagnostic_item("poll_wait_ms", 'Wait for result', _format_ms(p95.get("poll_wait_ms")), 'Interval / backoff', "warning"),
                _diagnostic_item("poll_request_ms", 'Query result', _format_ms(p95.get("poll_request_ms")), "task / conversation", "info"),
                _diagnostic_item("resolve_ms", 'Process result', _format_ms(p95.get("resolve_ms")), 'file ID / download URL', "warning"),
                _diagnostic_item("download_ms", 'Image download', _format_ms(p95.get("download_ms")), 'Download and return'),
                _diagnostic_item("response_ms", 'Format response', _format_ms(p95.get("response_ms")), 'Format API response'),
                _diagnostic_item("stream_ms", 'Protocol processing P95', _format_ms(p95.get("stream_ms")), 'Full image protocol processing', "info"),
            ],
        },
    ]


def build_monitor_view(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    threadpool_source = _mapping(snapshot.get("threadpool"))
    window_source = _mapping(snapshot.get("window"))
    threadpool = {
        "tokens": _int(threadpool_source.get("tokens")),
        "previous_tokens": _int(threadpool_source.get("previous_tokens")),
    }
    window = {
        "completed": _int(window_source.get("completed")),
        "completed_capacity": _int(window_source.get("completed_capacity")),
        "events": _int(window_source.get("events")),
        "event_capacity": _int(window_source.get("event_capacity")),
    }
    summary = _project_summary(snapshot.get("summary"))
    completed_window_text = f"Window {window['completed']} / {window['completed_capacity']}"
    return {
        "schema_version": MONITOR_SCHEMA_VERSION,
        "updated_at": str(snapshot.get("updated_at") or ""),
        "threadpool": threadpool,
        "window": window,
        "summary": summary,
        "active": [_project_record(item) for item in snapshot.get("active", []) if isinstance(item, Mapping)],
        "recent": [_project_record(item) for item in snapshot.get("recent", []) if isinstance(item, Mapping)],
        "slow": [_project_record(item) for item in snapshot.get("slow", []) if isinstance(item, Mapping)],
        "metric_labels": {str(key): str(label) for key, label in _mapping(snapshot.get("metric_labels")).items()},
        "completed_window_text": completed_window_text,
        "entry_queue_text": _format_ms(summary["entry_queue_p95_ms"]),
        "active_stage_items": [
            {"label": str(label), "count": _int(count)}
            for label, count in list(summary["active_by_stage"].items())[:8]
            if _int(count) > 0
        ],
        "diagnostic_groups": _build_diagnostic_groups(summary, threadpool["tokens"], completed_window_text),
    }


def build_monitor_record_view(record: Mapping[str, Any]) -> dict[str, Any]:
    return _project_record(record, include_detail=True)
