from __future__ import annotations

from typing import Any, Iterable, Mapping

from services.image_failure import (
    is_rate_limit_failure_code,
    is_structured_failure,
    is_text_review_failure_code,
)
from services.request_detail_view import (
    build_request_detail_core,
    build_request_timeline_presentation,
    format_request_duration,
    request_image_resolutions,
    request_status_presentation,
)


_SUMMARY_ERROR_LIMIT = 1000

_IMAGE_FAILURE_LABELS = {
    "upstream_error": 'Upstream request failed',
    "internal_error": 'Internal processing error',
    "upstream_unavailable": 'Upstream service is temporarily unavailable',
    "upstream_connection_failed": 'Could not connect to the upstream service',
    "upstream_connection_timeout": 'Upstream connection timed out',
    "upstream_rate_limited": 'Upstream rate limited',
    "image_poll_timeout": 'Timed out waiting for the image result',
    "image_stream_timeout": 'Upstream image stream timed out',
    "image_stream_interrupted": 'Upstream image stream was interrupted',
    "image_tool_error": 'Image tool error',
    "image_quota_exhausted": 'Image quota exhausted',
    "file_upload_throttled": 'Reference image upload was restricted',
    "auth_invalid": 'Account login session expired',
    "content_policy_violation": 'Rejected by the content safety policy',
    "invalid_image_input": 'Invalid image input',
    "upstream_text_reply": 'The upstream service returned text only',
    "no_image_generated": 'No image was generated',
    "unsupported_model": 'The model does not support image generation',
    "image_download_failed": 'Image download failed',
    "task_interrupted": 'Image task was interrupted',
    "no_available_account": 'No available account',
    "insufficient_quota": 'Insufficient image quota',
}

_BUSINESS_LABELS = {
    "account": 'Account operation',
    "image_generation": 'Text-to-image',
    "image_edit": 'Image-to-image',
    "image_chat": 'Chat image generation',
    "chat": 'Chat',
    "responses": 'Response',
    "messages": 'Message',
    "search": 'Search',
    "file": 'File',
}

def _record(value: object) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _detail(item: Mapping[str, Any]) -> dict[str, Any]:
    detail = item.get("detail")
    return _record(detail) if isinstance(detail, Mapping) else dict(item)


def _value(item: Mapping[str, Any], key: str, default: object = "") -> object:
    detail = item.get("detail")
    if isinstance(detail, Mapping):
        value = detail.get(key)
        if value not in (None, ""):
            return value
    value = item.get(key)
    return default if value in (None, "") else value


def _clean(value: object) -> str:
    return str(value or "").strip()


def _image_failure_label(value: object) -> str:
    return _IMAGE_FAILURE_LABELS.get(_clean(value).lower(), "")


def _normalize_account_status(value: object) -> str:
    status = _clean(value)
    aliases = {
        'Normal': 'Normal',
        "normal": 'Normal',
        "ready": 'Normal',
        "success": 'Normal',
        "completed": 'Normal',
        "complete": 'Normal',
        "done": 'Normal',
        'Rate limited': 'Rate limited',
        "limited": 'Rate limited',
        "rate_limited": 'Rate limited',
        "cooling": 'Rate limited',
        "backoff": 'Rate limited',
        'Abnormal': 'Abnormal',
        "abnormal": 'Abnormal',
        "invalid": 'Abnormal',
        "error": 'Abnormal',
        "failed": 'Abnormal',
        "fail": 'Abnormal',
        "incomplete": 'Abnormal',
        'Disabled': 'Disabled',
        "disabled": 'Disabled',
    }
    return aliases.get(status.lower(), status)


def _int(value: object) -> int:
    try:
        parsed = int(float(value or 0))
    except (TypeError, ValueError):
        return 0
    return max(0, parsed)


def _optional_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value == 1:
            return True
        if value == 0:
            return False
        return None
    normalized = str(value or "").strip().lower()
    if normalized in {"1", "true", "yes", "on", 'Yes'}:
        return True
    if normalized in {"0", "false", "no", "off", 'No'}:
        return False
    return None


def _bool(value: object) -> bool:
    return _optional_bool(value) is True


def _first_text(item: Mapping[str, Any], keys: Iterable[str]) -> str:
    for key in keys:
        value = _value(item, key)
        if text := _clean(value):
            return text
    return ""


def _known_url(value: object) -> str:
    text = _clean(value)
    if text.startswith(("http://", "https://", "/images/", "/image-thumbnails/")):
        return text
    return ""


def _urls_from(value: object) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    urls: list[str] = []
    for item in value:
        if isinstance(item, Mapping):
            url = _known_url(item.get("url"))
        else:
            url = _known_url(item)
        if url and url not in urls:
            urls.append(url)
    return urls


def call_image_urls(item: Mapping[str, Any]) -> list[str]:
    detail = _detail(item)
    urls: list[str] = []
    for key in ("image_urls", "urls", "result_urls", "_image_urls", "data"):
        for url in _urls_from(detail.get(key)):
            if url not in urls:
                urls.append(url)
    return urls


def call_business_kind(item: Mapping[str, Any]) -> str:
    log_type = _clean(item.get("type") or _value(item, "type")).lower()
    endpoint = _clean(_value(item, "endpoint")).lower().rstrip("/")
    model = _clean(_value(item, "model")).lower()
    image_request = _bool(_value(item, "image_request"))

    if log_type == "account":
        return "account"
    if endpoint.endswith("/images/generations"):
        return "image_generation"
    if endpoint.endswith("/images/edits"):
        return "image_edit"
    if image_request:
        return "image_chat"
    if endpoint.endswith("/chat/completions"):
        return "image_chat" if "image" in model else "chat"
    if endpoint.endswith("/responses"):
        return "responses"
    if endpoint.endswith("/messages"):
        return "messages"
    if "search" in endpoint:
        return "search"
    if "file" in endpoint:
        return "file"
    return "other"


def _attempt_items(item: Mapping[str, Any]) -> list[dict[str, Any]]:
    attempts = _value(item, "image_attempts", [])
    if not isinstance(attempts, list):
        return []
    normalized: list[dict[str, Any]] = []
    for value in attempts:
        if not isinstance(value, Mapping):
            continue
        attempt = dict(value)
        attempt["slot"] = max(1, _int(attempt.get("slot")))
        attempt["attempt"] = max(1, _int(attempt.get("attempt")))
        if "switched_account" in attempt:
            attempt["switched_account"] = _optional_bool(attempt.get("switched_account"))
        normalized.append(attempt)
    return normalized


def call_switch_count(item: Mapping[str, Any]) -> int:
    attempts = _attempt_items(item)
    attempt_count = sum(1 for attempt in attempts if attempt.get("switched_account") is True)
    explicit_count = max(
        _int(_value(item, "switch_count")),
        _int(_value(item, "image_account_switch_count")),
    )
    return max(attempt_count, explicit_count)


def _explicit_int(item: Mapping[str, Any], key: str) -> int | None:
    detail = item.get("detail")
    if isinstance(detail, Mapping) and key in detail and detail.get(key) not in (None, ""):
        return _int(detail.get(key))
    if key in item and item.get(key) not in (None, ""):
        return _int(item.get(key))
    return None


def call_image_counts(item: Mapping[str, Any]) -> tuple[int, int, int, str]:
    business = call_business_kind(item)
    explicit_requested = _explicit_int(item, "image_requested_count")
    explicit_succeeded = _explicit_int(item, "image_succeeded_count")
    explicit_failed = _explicit_int(item, "image_failed_count")
    attempts = _attempt_items(item)

    request_meta = _value(item, "request_meta", {})
    request_meta = request_meta if isinstance(request_meta, Mapping) else {}
    monitor = _value(item, "monitor", {})
    monitor = monitor if isinstance(monitor, Mapping) else {}
    images = monitor.get("images") if isinstance(monitor.get("images"), Mapping) else {}

    requested = max(
        explicit_requested or 0,
        _int(request_meta.get("n")),
        max((_int(attempt.get("slot")) for attempt in attempts), default=0),
        max(
            (
                _int(image.get("total"))
                for image in images.values()
                if isinstance(image, Mapping)
            ),
            default=0,
        ),
    )
    succeeded_slots = {
        _int(attempt.get("slot"))
        for attempt in attempts
        if _clean(attempt.get("status")).lower() == "success" and _int(attempt.get("slot")) > 0
    }
    result_count = max(
        _int(_value(item, "result_data_count")),
        _int(_value(item, "result_url_count")),
        len(call_image_urls(item)),
    )
    if explicit_succeeded is not None:
        succeeded = explicit_succeeded
    elif succeeded_slots:
        succeeded = max(len(succeeded_slots), result_count)
    else:
        succeeded = result_count
    requested = max(requested, succeeded)

    if explicit_failed is not None:
        failed = explicit_failed
    else:
        failed = max(0, requested - succeeded)
    requested = max(requested, succeeded + failed)

    explicit_status = _clean(_value(item, "image_result_status")).lower()
    if explicit_status in {"success", "failed", "partial_success"}:
        result_status = explicit_status
    elif succeeded > 0 and failed > 0:
        result_status = "partial_success"
    elif succeeded > 0:
        result_status = "success"
    elif requested > 0:
        result_status = "failed"
    else:
        result_status = ""

    if business not in {"image_generation", "image_edit", "image_chat"} and not any(
        (explicit_requested, explicit_succeeded, explicit_failed, attempts, result_count)
    ):
        return 0, 0, 0, ""
    return requested, succeeded, failed, result_status


def call_outcome(item: Mapping[str, Any]) -> str:
    status = _clean(_value(item, "status")).lower()
    error_code = _clean(_value(item, "error_code", _value(item, "failure_code"))).lower()
    status_code = _int(_value(item, "status_code"))
    requested, succeeded, failed, result_status = call_image_counts(item)

    if call_business_kind(item) == "account":
        account_status = _normalize_account_status(status)
        if status_code == 429 or account_status == 'Rate limited':
            return "rate_limited"
        if status_code >= 400 or account_status == 'Abnormal':
            return "failed"
        if account_status == 'Normal':
            return "success"
        if account_status == 'Disabled':
            return "unknown"

    if status == "partial_success" or result_status == "partial_success" or (
        requested > 0 and succeeded > 0 and failed > 0
    ):
        return "partial_success"
    if status == "text_review" or status_code == 400 or is_text_review_failure_code(error_code):
        return "text_review"
    if status in {"success", "completed", "complete", "done"}:
        return "success"
    if status_code == 429 or is_rate_limit_failure_code(status) or is_rate_limit_failure_code(error_code):
        return "rate_limited"
    if status_code >= 400 or is_structured_failure(
        status=status,
        error=_value(item, "error"),
        error_code=_value(item, "error_code"),
        failure_code=_value(item, "failure_code"),
    ):
        return "failed"
    return "unknown"


def call_timings_ms(item: Mapping[str, Any]) -> dict[str, int]:
    detail = _detail(item)
    monitor = detail.get("monitor") if isinstance(detail.get("monitor"), Mapping) else {}
    sources: list[Mapping[str, Any]] = []
    for value in (detail.get("perf"), detail.get("metrics"), monitor.get("metrics")):
        if isinstance(value, Mapping):
            sources.append(value)
    images = monitor.get("images")
    if isinstance(images, Mapping):
        for image in images.values():
            if isinstance(image, Mapping) and isinstance(image.get("metrics"), Mapping):
                sources.append(image["metrics"])

    timings: dict[str, int] = {}
    for source in sources:
        for key, value in source.items():
            name = _clean(key)
            if not name.endswith("_ms"):
                continue
            milliseconds = _int(value)
            if milliseconds > 0:
                timings[name] = max(timings.get(name, 0), milliseconds)
    return timings


def _duration_ms(item: Mapping[str, Any]) -> int:
    explicit = _int(_value(item, "duration_ms"))
    if explicit:
        return explicit
    timings = call_timings_ms(item)
    return max(
        timings.get("total_ms", 0),
        timings.get("handler_exec_ms", 0),
        timings.get("stream_ms", 0),
    )


def _attempt_result_status(attempt: Mapping[str, Any], outcome: str | None = None) -> str:
    failure_scope = _clean(attempt.get("failure_scope")).lower()
    error_code = _clean(attempt.get("error_code") or attempt.get("failure_code")).lower()
    if failure_scope == "delivery" or (not failure_scope and error_code == "image_download_failed"):
        return "generated_but_delivery_failed"
    if (outcome or call_outcome(attempt)) == "success":
        return "success"
    return "failed"


def _attempt_timings_ms(attempt: Mapping[str, Any]) -> dict[str, int]:
    monitor = _record(attempt.get("monitor"))
    return {
        _clean(key): _int(metric)
        for key, metric in _record(monitor.get("metrics")).items()
        if _clean(key).endswith("_ms") and _int(metric) > 0
    }


def _attempt_duration_ms(
    attempt: Mapping[str, Any],
    timings: Mapping[str, int] | None = None,
) -> int:
    resolved_timings = timings if timings is not None else _attempt_timings_ms(attempt)
    return _int(attempt.get("duration_ms")) or max(
        _int(resolved_timings.get("total_ms")),
        _int(resolved_timings.get("stream_ms")),
        _int(resolved_timings.get("handler_exec_ms")),
    )


def build_attempt_summary(value: Mapping[str, Any]) -> dict[str, Any]:
    attempt = dict(value)
    outcome = call_outcome(attempt)
    error_code = _clean(attempt.get("error_code") or attempt.get("failure_code"))
    monitor = _record(attempt.get("monitor"))
    timings = _attempt_timings_ms(attempt)
    duration_ms = _attempt_duration_ms(attempt, timings)
    result_status = _attempt_result_status(attempt, outcome)
    error_label = _image_failure_label(error_code)
    if result_status == "generated_but_delivery_failed":
        status_presentation = {"label": 'Generation succeeded', "tone": "warning"}
    else:
        status_presentation = _status_presentation({"outcome": outcome})
    summary = {
        "slot": max(1, _int(attempt.get("slot"))),
        "attempt": max(1, _int(attempt.get("attempt"))),
        "account_email": _clean(attempt.get("account_email")),
        "conversation_id": _clean(attempt.get("conversation_id")),
        "status": _clean(attempt.get("status")),
        "outcome": outcome,
        "result_status": result_status,
        "duration_ms": duration_ms,
        "status_code": _int(attempt.get("status_code")),
        "error_code": error_code,
        "error_label": error_label,
        "public_error": _clean(attempt.get("public_error") or attempt.get("error")),
        "upstream_error": _clean(attempt.get("upstream_error") or attempt.get("raw_upstream_error")),
        "upstream_text": _clean(
            attempt.get("upstream_text")
            or attempt.get("raw_upstream_message")
            or attempt.get("upstream_message")
            or attempt.get("upstream_message_preview")
        ),
        "switched_account": _optional_bool(attempt.get("switched_account")),
        "timings_ms": timings,
        "monitor": monitor,
    }
    summary["presentation"] = {
        "status": status_presentation,
        "failure_label": error_label or (
            'Result delivery failed'
            if result_status == "generated_but_delivery_failed"
            else 'Generation failed'
        ),
        "marker_tone": "success" if result_status == "success" else "danger",
        "switch_label": 'Switched account' if summary["switched_account"] is True else "",
        "error_code_text": error_code,
        "status_code_text": f"HTTP {summary['status_code']}" if summary["status_code"] else "",
        "show_failure": result_status != "success",
        "show_error_details": bool(
            summary["public_error"]
            or summary["upstream_error"]
            or summary["upstream_text"]
        ),
        "timeline": build_request_timeline_presentation(
            timings,
            monitor.get("events"),
            image_count=1,
        ),
    }
    return summary


def _type_label(log_type: object) -> str:
    value = _clean(log_type)
    if value == "call":
        return 'API call logs'
    if value == "account":
        return 'Account logs'
    return value or 'Logs'


def _business_label(business: object, log_type: object) -> str:
    return _BUSINESS_LABELS.get(_clean(business), _type_label(log_type))


_format_duration = format_request_duration


def _duration_breakdown(attempts: list[dict[str, Any]]) -> str:
    ordered_attempts = sorted(
        attempts,
        key=lambda attempt: (_int(attempt.get("slot")), _int(attempt.get("attempt"))),
    )
    attempts_by_slot: dict[int, list[int]] = {}
    for attempt in ordered_attempts:
        duration_ms = _attempt_duration_ms(attempt)
        if duration_ms <= 0:
            continue
        slot = _int(attempt.get("slot"))
        attempts_by_slot.setdefault(slot, []).append(duration_ms)

    retry_groups = [
        (slot, durations)
        for slot, durations in sorted(attempts_by_slot.items())
        if len(durations) > 1
    ]
    if not retry_groups:
        return ""

    has_multiple_slots = len({_int(attempt.get("slot")) for attempt in attempts}) > 1
    expressions: list[str] = []
    for slot, durations in retry_groups:
        expression = " + ".join(_format_duration(duration) for duration in durations)
        expressions.append(f"Image {slot}：{expression}" if has_multiple_slots else expression)
    return f"({'；'.join(expressions)})"


def _status_presentation(summary: Mapping[str, Any]) -> dict[str, str]:
    outcome = _clean(summary.get("outcome"))
    display_status = _clean(summary.get("display_status"))
    if _clean(summary.get("business")) == "account" and display_status:
        tones = {'Normal': "success", 'Abnormal': "danger", 'Rate limited': "warning", 'Disabled': "muted"}
        return {"label": display_status, "tone": tones.get(display_status, "muted")}
    return request_status_presentation(outcome, fallback=display_status or 'Record')


def _result_text(summary: Mapping[str, Any]) -> str:
    outcome = _clean(summary.get("outcome"))
    requested = _int(summary.get("image_requested_count"))
    succeeded = _int(summary.get("image_succeeded_count"))
    public_error = _clean(summary.get("public_error"))
    error_label = _image_failure_label(summary.get("error_code"))
    summary_text = _clean(summary.get("summary"))

    if outcome == "partial_success":
        return f"Generated {succeeded}/{requested} images"
    if outcome == "text_review":
        return 'Upstream response text'
    if outcome in {"failed", "rate_limited"}:
        return public_error or error_label or summary_text or 'Call failed'
    if succeeded > 0:
        return (
            f"Generated {succeeded}/{requested} images"
            if requested > 1
            else f"Generated {succeeded} images"
        )
    if outcome == "success":
        business = _clean(summary.get("business"))
        if business in {"image_generation", "image_edit", "image_chat"}:
            return 'Image generation completed'
        if business == "search":
            return 'Search completed'
        if business in {"chat", "responses", "messages"}:
            return 'Text response completed'
        if business == "account":
            return summary_text or 'Account operation completed'
        return 'Call completed'
    return summary_text or public_error or 'Call completed'


def _build_presentation(
    summary: Mapping[str, Any],
    attempts: list[dict[str, Any]],
    detail: Mapping[str, Any],
) -> dict[str, Any]:
    outcome = _clean(summary.get("outcome"))
    log_type = _clean(summary.get("type"))
    business = _clean(summary.get("business"))
    task_count = _int(summary.get("image_requested_count"))
    attempt_count = _int(summary.get("attempt_count"))
    caller = _clean(summary.get("key_name") or summary.get("key_id"))
    execution_parts = [
        f"{task_count} tasks" if task_count > 0 else "",
        f"{attempt_count} attempts" if attempt_count > 0 else "",
    ]
    execution_primary = " · ".join(part for part in execution_parts if part) or caller or "-"
    show_failure_details = outcome in {"failed", "rate_limited"}
    diagnostics = " · ".join(
        part
        for part in (
            f"HTTP {_int(summary.get('status_code'))}"
            if show_failure_details and _int(summary.get("status_code")) > 0
            else "",
            _clean(summary.get("error_code")) if show_failure_details else "",
        )
        if part
    )
    summary_text = _clean(summary.get("summary"))
    if outcome == "text_review" and summary_text:
        summary_text = summary_text.replace('Streaming call failed', 'Text').replace('Call failed', 'Text')
    if not summary_text:
        summary_text = _clean(summary.get("public_error"))

    duration_ms = _int(summary.get("duration_ms"))
    request_meta = _record(detail.get("request_meta"))
    image_parameters = " · ".join(
        f"{label} {_clean(request_meta[key])}"
        for key, label in (("size", 'Request'), ("quality", 'Quality'), ("response_format", 'Output'))
        if _clean(request_meta.get(key))
    )
    resolutions = dict.fromkeys(request_image_resolutions(detail))
    return {
        "request": {
            "kind": "" if log_type == "account" else _business_label(business, log_type),
            "primary": _clean(summary.get("model")) or _type_label(log_type),
            "secondary": _clean(summary.get("endpoint")),
            "parameters": image_parameters,
        },
        "execution": {
            "primary": execution_primary,
            "secondary": caller if task_count > 0 else "",
        },
        "status": _status_presentation(summary),
        "result": {
            "text": _result_text(summary),
            "diagnostics": diagnostics,
            "resolution": " / ".join(resolutions),
        },
        "summary_text": summary_text,
        "duration": {
            "text": _format_duration(duration_ms),
            "breakdown": _duration_breakdown(attempts),
            "tone": (
                "danger"
                if outcome == "failed"
                else "warning"
                if duration_ms >= 60000
                else "success"
            ),
        },
        "is_failure": outcome == "failed",
    }


def _attempt_group_presentations(
    attempts: list[dict[str, Any]],
    requested_count: int,
) -> list[dict[str, Any]]:
    grouped: dict[int, list[dict[str, Any]]] = {}
    for attempt in attempts:
        slot = max(1, _int(attempt.get("slot")))
        grouped.setdefault(slot, []).append(attempt)

    result: list[dict[str, Any]] = []
    slot_count = max(requested_count, max(grouped, default=0))
    for slot in range(1, slot_count + 1):
        slot_attempts = grouped.get(slot, [])
        attempt_count = len(slot_attempts)
        switch_count = sum(1 for attempt in slot_attempts if attempt.get("switched_account") is True)
        succeeded = any(_clean(attempt.get("result_status")) == "success" for attempt in slot_attempts)
        delivery_failed = any(
            _clean(attempt.get("result_status")) == "generated_but_delivery_failed"
            for attempt in slot_attempts
        )
        if succeeded:
            status = {"label": 'Succeeded', "tone": "success"}
        elif delivery_failed:
            status = {"label": 'Generation succeeded', "tone": "warning"}
        elif slot_attempts:
            status = {"label": 'Failed', "tone": "danger"}
        else:
            status = {"label": 'Not recorded', "tone": "muted"}
        result.append(
            {
                "slot": slot,
                "slot_label": f"Image {slot}",
                "attempt_count": attempt_count,
                "attempt_text": f"{attempt_count} attempts",
                "switch_count": switch_count,
                "switch_text": f"Switched {switch_count} times" if switch_count else "",
                "status": status,
            }
        )
    return result


def _build_detail_presentation(
    summary: Mapping[str, Any],
    detail: Mapping[str, Any],
    monitor: Mapping[str, Any],
    attempts: list[dict[str, Any]],
    timings: Mapping[str, int],
    image_count: int,
) -> dict[str, Any]:
    requested_count = _int(summary.get("image_requested_count"))
    has_delivery_failure = any(
        _clean(attempt.get("result_status")) == "generated_but_delivery_failed"
        for attempt in attempts
    )
    has_attempt_breakdown = (
        bool(attempts)
        and (
            len(attempts) > 1
            or requested_count > 1
            or has_delivery_failure
        )
    )
    identity_lives_in_attempts = len(attempts) > 1 or requested_count > 1
    core = build_request_detail_core(
        summary,
        detail,
        monitor,
        timings,
        events=monitor.get("events"),
        image_count=image_count,
        request_shape=detail.get("request_shape"),
        hide_account_identity=identity_lives_in_attempts,
        suppress_timeline=has_attempt_breakdown,
    )
    return {
        **core,
        "has_attempt_breakdown": has_attempt_breakdown,
        "attempt_groups": (
            _attempt_group_presentations(attempts, requested_count)
            if has_attempt_breakdown
            else []
        ),
    }


def build_call_summary(item: Mapping[str, Any], *, error_limit: int = _SUMMARY_ERROR_LIMIT) -> dict[str, Any]:
    requested, succeeded, failed, result_status = call_image_counts(item)
    attempts = _attempt_items(item)
    switch_count = call_switch_count(item)
    outcome = call_outcome(item)
    business = call_business_kind(item)
    display_status = _clean(_value(item, "status"))
    if business == "account":
        display_status = _normalize_account_status(display_status)
    public_error = _first_text(item, ("public_error", "error"))
    if error_limit > 0 and len(public_error) > error_limit:
        public_error = f"{public_error[:error_limit]}..."
    image_urls = call_image_urls(item)
    summary = {
        "id": _clean(item.get("id") or _value(item, "call_id")),
        "time": _clean(item.get("time") or _value(item, "started_at")),
        "type": _clean(item.get("type") or "call"),
        "summary": _clean(item.get("summary")),
        "business": business,
        "outcome": outcome,
        "display_status": display_status,
        "endpoint": _clean(_value(item, "endpoint")),
        "model": _clean(_value(item, "model")),
        "started_at": _clean(_value(item, "started_at")),
        "ended_at": _clean(_value(item, "ended_at")),
        "duration_ms": _duration_ms(item),
        "key_id": _clean(_value(item, "key_id")),
        "key_name": _clean(_value(item, "key_name")),
        "role": _clean(_value(item, "role")),
        "account_email": _clean(_value(item, "account_email")),
        "conversation_id": _clean(_value(item, "conversation_id")),
        "status_code": _int(_value(item, "status_code")),
        "error_code": _clean(_value(item, "error_code", _value(item, "failure_code"))),
        "public_error": public_error,
        "image_requested_count": requested,
        "image_succeeded_count": succeeded,
        "image_failed_count": failed,
        "image_result_status": result_status,
        "preview_image_url": image_urls[0] if image_urls else "",
        "attempt_count": len(attempts),
        "switch_count": switch_count,
        "recovered_after_switch": switch_count > 0 and outcome in {"success", "partial_success"},
    }
    summary["presentation"] = _build_presentation(summary, attempts, _detail(item))
    return summary


def build_call_detail(item: Mapping[str, Any]) -> dict[str, Any]:
    detail = _detail(item)
    monitor = _record(detail.get("monitor"))
    summary = build_call_summary(item)
    attempts = [build_attempt_summary(value) for value in _attempt_items(item)]
    timings = call_timings_ms(item)
    image_urls = call_image_urls(item)
    return {
        **summary,
        "request_text": _clean(detail.get("request_text")),
        "request_text_full": _clean(detail.get("request_text_full")),
        "request_text_truncated": _bool(detail.get("request_text_truncated")),
        "request_shape": _record(detail.get("request_shape")),
        "request_meta": _record(detail.get("request_meta")),
        "upstream_error": _clean(
            detail.get("upstream_error")
            or detail.get("raw_upstream_error")
            or monitor.get("upstream_error")
            or monitor.get("raw_upstream_error")
        ),
        "upstream_text": _clean(
            detail.get("upstream_text")
            or detail.get("raw_upstream_message")
            or detail.get("upstream_message")
            or detail.get("upstream_message_preview")
            or detail.get("upstream_preview")
            or monitor.get("upstream_text")
            or monitor.get("raw_upstream_message")
            or monitor.get("upstream_message")
            or monitor.get("upstream_message_preview")
            or monitor.get("upstream_preview")
        ),
        "image_urls": image_urls,
        "attempts": attempts,
        "timings_ms": timings,
        "perf": _record(detail.get("perf")),
        "metrics": _record(detail.get("metrics")),
        "monitor": monitor,
        "detail_presentation": _build_detail_presentation(
            summary,
            detail,
            monitor,
            attempts,
            timings,
            len(image_urls),
        ),
        "raw_detail": detail,
    }
