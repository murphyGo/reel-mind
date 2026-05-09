"""Structured logging and redaction helpers."""

from __future__ import annotations

import atexit
import re
import sys
from collections.abc import Mapping, MutableMapping
from typing import Any, cast

import structlog

SECRET_PATTERN = re.compile(
    r"(?i)\b(authorization)\s*[:=]\s*(?:bearer\s+)?[^\s,;'\"\]]+"
    r"|\b(bearer|token|secret|api[_-]?key|refresh[_-]?token)\s*[:=]\s*[^\s,;'\"\]]+"
)


class RedactionProcessor:
    deny_keys = frozenset(
        {
            "api_key",
            "token",
            "secret",
            "refresh_token",
            "authorization",
            "email",
            "telegram_chat_id",
        }
    )

    def __call__(
        self,
        logger: Any,
        method_name: str,
        event_dict: MutableMapping[str, Any],
    ) -> Mapping[str, Any]:
        return cast(Mapping[str, Any], redact_value(event_dict))


def redact_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if key_text.lower() in RedactionProcessor.deny_keys:
                redacted[key_text] = _mask(item)
            else:
                redacted[key_text] = redact_value(item)
        return redacted
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_value(item) for item in value)
    if isinstance(value, str):
        return SECRET_PATTERN.sub(_redact_match, value)
    return value


def _mask(value: Any) -> str:
    if isinstance(value, str) and value.startswith("***(len="):
        return value
    return f"***(len={len(str(value))})"


def _redact_match(match: re.Match[str]) -> str:
    key = match.group(1) or match.group(2)
    return f"{key}: ***"


def init_logger(service: str) -> structlog.BoundLogger:
    atexit.register(sys.stdout.flush)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
            _add_static_context(service),
            RedactionProcessor(),
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(sort_keys=True),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(0),
        cache_logger_on_first_use=True,
    )
    return cast(structlog.BoundLogger, structlog.get_logger(service=service))


def get_logger() -> structlog.BoundLogger:
    return cast(structlog.BoundLogger, structlog.get_logger())


def _add_static_context(service: str) -> Any:
    def processor(logger: Any, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
        event_dict.setdefault("service", service)
        event_dict.setdefault(
            "python_version",
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        )
        return event_dict

    return processor
